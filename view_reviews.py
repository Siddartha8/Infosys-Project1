import sqlite3
from tabulate import tabulate

# Connect to your database
conn = sqlite3.connect("instance/reviews.db")
cursor = conn.cursor()

# Run query
cursor.execute("SELECT * FROM review")
rows = cursor.fetchall()

# Get column names
columns = [description[0] for description in cursor.description]

# Print as table
print(tabulate(rows, headers=columns, tablefmt="grid"))

conn.close()
