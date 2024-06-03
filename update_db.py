import sqlite3

conn = sqlite3.connect('hospital.db')
cursor = conn.cursor()

# Add the status column to Appointments table
cursor.execute('ALTER TABLE Appointments ADD COLUMN status TEXT DEFAULT "Pending"')

conn.commit()
conn.close()
