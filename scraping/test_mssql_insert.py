"""test_mssql_insert.py
Quick sanity-check that `mssql_utils.save_annuity_data_to_mssql` correctly
creates the database/table and inserts rows.

Run:
    python test_mssql_insert.py

Make sure your SQL Server container is up and listening on localhost:1433 with
user=sa / password=AppPass123$.
"""

from mssql_utils import save_annuity_data_to_mssql

# Dummy data – covers INT, DECIMAL and TEXT inference
DATA = [
    {
        "Company_Product_Name": "Dummy Co – MyGA 1",
        "AM_Best": "A-",
        "Max_Issue_Age": "85",
        "Min_Premium": "10,000",
        "Current_Rate": "4.25",
        "Years": "1 yr",
    },
    {
        "Company_Product_Name": "Dummy Co – MyGA 2",
        "AM_Best": "B+",
        "Max_Issue_Age": "90",
        "Min_Premium": "5000",
        "Current_Rate": "5.00",
        "Years": "2 yrs",
    },
]

DB_CONFIG = {
    "host": "localhost",
    "port": 1433,
    "user": "sa",
    "password": "TestPass123!",
    "database": "annuity_data_test",
}

def main():
    print("🚀 Inserting dummy data into SQL Server…")
    save_annuity_data_to_mssql(DATA, DB_CONFIG, table_name="annuities_test", recreate_table=True)
    print("✅ Test complete – inspect annuity_data_test.annuities_test table.")


if __name__ == "__main__":
    main()
