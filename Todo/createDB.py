import sqlite3


con = sqlite3.connect("todo.db")


con.execute("CREATE TABLE tasks(id INTEGER NOT NULL,task TEXT NOT NULL,due TEXT NOT NULL,status TEXT NOT NULL, primary key(id))")

con.execute("insert into tasks values (1, 'Complete Task 1', '2022-11-21', 'Not Started')")
con.execute("insert into tasks values (2, 'Complete Task 2', '2022-11-23', 'In Progress')")
con.execute("insert into tasks values (3, 'Complete Task 3', '2022-11-25', 'Finished')")
con.execute("insert into tasks values (4, 'Complete Task 4', '2022-11-28', 'In Progress')")
con.execute("insert into tasks values (5, 'Complete Task 5', '2022-11-29', 'Not Started')")

con.commit()
con.close()
