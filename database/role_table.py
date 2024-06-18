import mysql.connector

# Establishing the connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="absensi"
)

# Creating a cursor object to interact with the database
cursor = db.cursor()

# Query to create the table
create_table_query = """
CREATE TABLE IF NOT EXISTS roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

try:
    # Executing the query
    cursor.execute(create_table_query)
    # Committing the changes
    db.commit()
    print("Table 'roles' created successfully.")
except mysql.connector.Error as err:
    print(f"Error: {err.msg}")
finally:
    # Closing the cursor and the connection
    cursor.close()
    db.close()
