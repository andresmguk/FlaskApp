# flasktaskr/db_create.py

# imports
import sqlite3
from _config import DATABASE_PATH


# Connect to the database
with sqlite3.connect(DATABASE_PATH) as connection:

	# get a cursor object to execute SQL commands
	c = connection.cursor()

	# create the table (5 rows)
	c.execute("""CREATE TABLE tasks(task_id INTEGER PRIMARY KEY AUTOINCREMENT, 
		name TEXT NOT NULL, due_date TEXT NOT NULL,
		priority INTEGER NOT NULL, status INTEGER NOT NULL)""")

	# insert dummy data in the table
	c.execute(
			'INSERT INTO tasks (name, due_date, priority, status)'
			'VALUES("Finish this tutorial", "03/05/2015", 10, 1)'
	)

	c.execute(
			'INSERT INTO tasks (name, due_date, priority, status)'
			'VALUES("Master flask basics", "01/09/2016", 10, 1)'
	)

