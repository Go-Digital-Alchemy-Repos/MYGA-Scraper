"""mssql_utils.py
Utility helpers for persisting scraped annuity data into a Microsoft SQL Server
database (tested with SQL Server 2019 & ODBC Driver 18).

Install system driver:
  macOS:  brew tap microsoft/mssql-release && \
          ACCEPT_EULA=Y brew install msodbcsql18
  Ubuntu: https://learn.microsoft.com/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server

Plus Python deps:
  pip install pyodbc
"""
from __future__ import annotations

import re
from typing import List, Dict, Sequence, Optional
from decimal import Decimal
import pyodbc

DEFAULT_COLUMN_TYPE = "NVARCHAR(MAX)"
NUMERIC_DECIMAL_TYPE = "DECIMAL(20,6)"


def _infer_column_types(data: List[Dict], columns: Sequence[str]) -> Dict[str, str]:
    """Infer INT or DECIMAL columns by inspecting values."""
    types: Dict[str, str] = {}
    int_regex = re.compile(r"^\d+$")
    dec_regex = re.compile(r"^\d+\.\d+$")
    for col in columns:
        inferred: Optional[str] = None
        for row in data:
            v = row.get(col)
            if v in (None, "", "-", "N/A"):
                continue
            if isinstance(v, int):
                candidate = "INT"
            elif isinstance(v, float):
                candidate = NUMERIC_DECIMAL_TYPE
            else:
                s = str(v).replace(",", "").strip()
                if int_regex.fullmatch(s):
                    candidate = "INT"
                elif dec_regex.fullmatch(s):
                    candidate = NUMERIC_DECIMAL_TYPE
                else:
                    inferred = None
                    break
            if inferred is None:
                inferred = candidate
            elif inferred == "INT" and candidate == NUMERIC_DECIMAL_TYPE:
                inferred = NUMERIC_DECIMAL_TYPE
        if inferred:
            types[col] = inferred
    return types


def _convert(value, col_type: str):
    if value in (None, "", "-", "N/A"):
        return None
    try:
        if col_type == "INT":
            return int(str(value).replace(",", ""))
        if col_type.startswith("DECIMAL"):
            return float(str(value).replace(",", ""))
    except Exception:
        return None
    return None


def save_annuity_data_to_mssql(
    data: List[Dict],
    db_config: Dict[str, str],
    *,
    table_name: str = "annuities",
    explicit_columns: Optional[Sequence[str]] = None,
    column_type_overrides: Optional[Dict[str, str]] = None,
    recreate_table: bool = True,
):
    """Save annuity data (list of dicts) into SQL Server."""
    if not data:
        print("⚠️  No data to save – skipping.")
        return

    # Columns
    if explicit_columns is None:
        col_set = set()
        for row in data:
            col_set.update(row.keys())
        columns = sorted(col_set)
    else:
        columns = list(explicit_columns)

    inferred = _infer_column_types(data, columns)
    if column_type_overrides:
        inferred.update(column_type_overrides)

    # Apply default overrides for known numeric columns
    default_numeric = {
        "Min_Premium": "INT",
        "Max_Issue_Age": "INT",
        "Current_Rate": NUMERIC_DECIMAL_TYPE,
        "Base_Rate": NUMERIC_DECIMAL_TYPE,
        "GTD_Yield_Rate": NUMERIC_DECIMAL_TYPE,
    }
    for col, typ in default_numeric.items():
        if col in columns and col not in inferred:
            inferred[col] = typ

    # Build connection string
    conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={db_config.get('host','localhost')},"
        f"{db_config.get('port', 1433)};UID={db_config['user']};PWD={db_config['password']};"
        f"TrustServerCertificate=Yes;"
    )
    database = db_config.get("database", "annuity_data")

    with pyodbc.connect(conn_str, autocommit=True) as master_conn:
        master_cursor = master_conn.cursor()
        master_cursor.execute(f"IF DB_ID('{database}') IS NULL CREATE DATABASE [{database}]")

    conn_str_db = conn_str + f"DATABASE={database};"
    with pyodbc.connect(conn_str_db, autocommit=True) as conn:
        cur = conn.cursor()
        if recreate_table:
            cur.execute(f"IF OBJECT_ID('{table_name}', 'U') IS NOT NULL DROP TABLE [{table_name}]")

        # create table
        col_defs = [
            f"[{c}] {inferred.get(c, DEFAULT_COLUMN_TYPE)}" for c in columns
        ]
        # SQL Server doesn't support 'IF NOT EXISTS' within CREATE TABLE.
        # Use a conditional wrapper or assume table was dropped already.
        create_sql = (
            f"IF OBJECT_ID('{table_name}', 'U') IS NULL "
            f"CREATE TABLE [{table_name}] (id INT IDENTITY(1,1) PRIMARY KEY, {', '.join(col_defs)})"
        )
        cur.execute(create_sql)

        # insert rows
        placeholders = ", ".join(["?"] * len(columns))
        col_names_sql = ", ".join(f"[{c}]" for c in columns)
        insert_sql = f"INSERT INTO [{table_name}] ({col_names_sql}) VALUES ({placeholders})"
        rows = [tuple(_convert(row.get(c), inferred.get(c, DEFAULT_COLUMN_TYPE)) for c in columns) for row in data]
        cur.fast_executemany = True  # speed up bulk insert
        cur.executemany(insert_sql, rows)
        print(f"💾  Inserted {cur.rowcount} rows into {database}.{table_name}")
