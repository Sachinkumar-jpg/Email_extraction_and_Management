import json
import mysql.connector

# --- Step 1: MySQL base connection (no database yet) ---
base_config = {
    "host": "localhost",
    "user": "user_name",
    "password": "yourSQLpassword"
}

DB_NAME = "email_data"
TABLE_NAME = "job_application"

# Connect without DB to create DB if needed
conn = mysql.connector.connect(**base_config)
cursor = conn.cursor()

# --- Step 2: Create database if it doesn't exist ---
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
print(f"✅ Database `{DB_NAME}` ensured.")

# Switch to the created database
cursor.execute(f"USE {DB_NAME}")

# --- Step 3: Create table if it doesn't exist ---
cursor.execute(f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(255),
    date_applied DATE,
    days_since_update INT,
    role_applied_for VARCHAR(255),
    status VARCHAR(100)
)
""")
print(f"✅ Table `{TABLE_NAME}` ensured.")

# --- Step 4: Load JSON data ---
with open("email_applications.json", "r") as f:
    data = json.load(f)

# --- Step 5: Insert data ---
insert_query = f"""
INSERT INTO {TABLE_NAME}
(company_name, date_applied, days_since_update, role_applied_for, status)
VALUES (%s, %s, %s, %s, %s)
"""

for row in data:
    cursor.execute(insert_query, (
        row["company_name"],
        row["date_applied"],
        row["days_since_update"],
        row["role_applied_for"],
        row["status"]
    ))

conn.commit()
cursor.close()
conn.close()

print("✅ All data inserted into MySQL successfully.")
