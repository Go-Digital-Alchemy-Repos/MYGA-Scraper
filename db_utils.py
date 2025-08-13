"""db_utils.py
Utility helpers for persisting scraped annuity data into a MySQL database.

Usage:
    from db_utils import save_annuity_data_to_mysql
    save_annuity_data_to_mysql(data, {
        "host": "localhost",
        "user": "root",
        "password": "password",
        "database": "annuity_data"
    }, table_name="annuities")

The helper will:
1. Connect to MySQL (creating the database if it does not exist)
2. Derive column names from the ``data`` list-of-dicts or use the supplied
   ``explicit_columns`` argument
3. Create a table with TEXT columns (flexible for string/numeric)
4. Bulk-insert the rows with one ``executemany`` call.

If you need stricter typing, pass a ``column_type_overrides`` dict mapping a
column name to a specific MySQL type (e.g. "Max_Issue_Age": "INT"). Any
columns missing from that mapping default to ``TEXT``.
"""

from __future__ import annotations

from typing import Dict, List, Sequence, Optional
import mysql.connector
from mysql.connector import errorcode, MySQLConnection
import re
from decimal import Decimal


DEFAULT_COLUMN_TYPE = "TEXT"
NUMERIC_DECIMAL_TYPE = "DECIMAL(20,6)"


def _infer_column_types(data: List[Dict], columns: Sequence[str]) -> Dict[str, str]:
    """Infer INT or DECIMAL columns by inspecting values.

    A column is considered INT if *all* non-empty values are integer-like
    (digits only, ignoring commas). It is considered DECIMAL when at least one
    value contains a decimal point but all values are still purely numeric.
    Otherwise falls back to TEXT.
    """
    types: Dict[str, str] = {}
    int_regex = re.compile(r"^\d+$")
    dec_regex = re.compile(r"^\d+\.\d+$")

    for col in columns:
        inferred: Optional[str] = None
        for row in data:
            v = row.get(col)
            if v in (None, "", "-", "N/A"):
                # empty value – ignore for type inference
                continue

            # if value already numeric (int/float), treat accordingly
            if isinstance(v, int):
                candidate = "INT"
            elif isinstance(v, float):
                candidate = NUMERIC_DECIMAL_TYPE
            else:
                # strip commas/spaces
                s = str(v).replace(",", "").strip()
                if int_regex.fullmatch(s):
                    candidate = "INT"
                elif dec_regex.fullmatch(s):
                    candidate = NUMERIC_DECIMAL_TYPE
                else:
                    inferred = None
                    break  # mixed content – not numeric
            # First numeric seen
            if inferred is None:
                inferred = candidate
            else:
                # Upgrade INT->DECIMAL if we encounter a decimal later
                if inferred == "INT" and candidate == NUMERIC_DECIMAL_TYPE:
                    inferred = NUMERIC_DECIMAL_TYPE
                # If mismatch (DECIMAL then INT) keep DECIMAL; it’s safe
                # If conflicting with TEXT => will have broken earlier
        if inferred:
            types[col] = inferred
    return types


def _convert_value_for_db(value, col_type: str):
    """Convert string numeric values into proper Python numeric types."""
    if value in (None, "", "-", "N/A"):
        return None
    try:
        if col_type == "INT":
            return int(str(value).replace(",", ""))
        if col_type.startswith("DECIMAL"):
            return float(str(value).replace(",", ""))
    except Exception:
        pass  # fallback to original value
    return value


def _connect(db_config: Dict[str, str], *, create_db: bool = True) -> MySQLConnection:
    """Connect to MySQL; create database if missing (when ``create_db``)."""
    # Connect without specifying database first so we can potentially CREATE it
    conn = mysql.connector.connect(
        host=db_config.get("host", "localhost"),
        user=db_config["user"],
        password=db_config["password"],
        port=db_config.get("port", 3306),
        autocommit=True,
    )
    cursor = conn.cursor()

    db_name = db_config["database"]
    if create_db:
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{db_name}` DEFAULT CHARACTER SET utf8mb4"
        )
    cursor.execute(f"USE `{db_name}`")
    cursor.close()
    return conn


def _ensure_table(
    cursor, table_name: str, columns: Sequence[str], column_type_overrides: Optional[Dict[str, str]] = None
):
    """Create the table if it does not exist.

    All columns default to TEXT unless overridden by *column_type_overrides*.
    """
    column_type_overrides = column_type_overrides or {}
    column_defs = []
    for col in columns:
        col_type = column_type_overrides.get(col, DEFAULT_COLUMN_TYPE)
        column_defs.append(f"`{col}` {col_type}")

    sql = (
        f"CREATE TABLE IF NOT EXISTS `{table_name}` (\n"
        "    id INT AUTO_INCREMENT PRIMARY KEY,\n"
        f"    {', '.join(column_defs)}\n"
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"
    )
    cursor.execute(sql)


def save_annuity_data_to_mysql(
    data: List[Dict],
    db_config: Dict[str, str],
    *,
    table_name: str = "annuities",
    explicit_columns: Optional[Sequence[str]] = None,
    column_type_overrides: Optional[Dict[str, str]] = None,
    recreate_table: bool = True,
):
    """Persist a list of annuity product dicts to MySQL.

    Parameters
    ----------
    data:
        List of dictionaries as returned by ``PaginatedSeleniumAnnuityRateWatchScraper``.
    db_config:
        Mapping with keys ``host``, ``user``, ``password``, and ``database``.
    table_name:
        Destination table name (default "annuities").
    explicit_columns:
        Optional explicit column ordering. If ``None``, columns are discovered
        from the keys present in *data*.
    column_type_overrides:
        Mapping of column name to MySQL type (e.g. {"Max_Issue_Age": "INT"}).
    recreate_table:
        If True (default) drops the existing table before recreating it so column type
        changes take effect. Set to False to append/merge into an existing table.
    """
    if not data:
        print("⚠️  No data to save to MySQL – skipping.")
        return

    # Derive columns
    if explicit_columns is None:
        col_set = set()
        for row in data:
            col_set.update(row.keys())
        columns = sorted(col_set)
    else:
        columns = list(explicit_columns)

    # Infer numeric types automatically
    inferred_types = _infer_column_types(data, columns)
    if column_type_overrides:
        inferred_types.update(column_type_overrides)  # explicit overrides win

    # Establish connection and ensure schema (drop table to apply new types)
    try:
        conn = _connect(db_config, create_db=True)
        cursor = conn.cursor()

        # Drop existing table so schema changes apply cleanly if requested
        if recreate_table:
            cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")

        _ensure_table(cursor, table_name, columns, inferred_types)

        # Prepare INSERT
        col_names_sql = ", ".join(f"`{c}`" for c in columns)
        placeholders = ", ".join(["%s"] * len(columns))
        insert_sql = f"INSERT INTO `{table_name}` ({col_names_sql}) VALUES ({placeholders})"

        # Prepare data rows with type conversion
        values = [
            tuple(
                _convert_value_for_db(row.get(col), inferred_types.get(col, DEFAULT_COLUMN_TYPE))
                for col in columns
            )
            for row in data
        ]

        cursor.executemany(insert_sql, values)
        conn.commit()
        print(f"💾  Inserted {cursor.rowcount} rows into {db_config['database']}.{table_name}")
    except mysql.connector.Error as exc:
        print(f"❌  MySQL error: {exc}")
        raise
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass