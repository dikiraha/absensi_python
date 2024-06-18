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
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_card VARCHAR(20) UNIQUE NOT NULL,
    nik VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    jabatan_id INT,
    department_id INT,
    role_id INT,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (jabatan_id) REFERENCES jabatans(id),
    FOREIGN KEY (department_id) REFERENCES departments(id),
    FOREIGN KEY (role_id) REFERENCES roles(id)
)
"""

try:
    # Executing the query
    cursor.execute(create_table_query)
    # Committing the changes
    db.commit()
    print("Table 'users' created successfully.")
except mysql.connector.Error as err:
    print(f"Error: {err.msg}")
finally:
    # Closing the cursor and the connection
    cursor.close()
    db.close()
