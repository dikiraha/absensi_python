import bcrypt
import mysql.connector

# Configure MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="attendance_db"
)

# Create a cursor
cursor = db.cursor()

# Define the username and password
username = "diki"
password = "diki"

# Hash the password using bcrypt
hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Insert the user into the user table
insert_query = """
    INSERT INTO user (username, password) 
    VALUES (%s, %s)
"""

cursor.execute(insert_query, (username, hashed_password))
db.commit()

print(f"User {username} created with hashed password.")

# Close the cursor and connection
cursor.close()
db.close()
