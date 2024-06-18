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
CREATE TABLE IF NOT EXISTS log_absens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    type VARCHAR(20) NOT NULL,
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
"""

try:
    # Executing the query
    cursor.execute(create_table_query)
    # Committing the changes
    db.commit()
    print("Table 'log_absen' created successfully.")
except mysql.connector.Error as err:
    print(f"Error: {err.msg}")
finally:
    # Closing the cursor and the connection
    cursor.close()
    db.close()
