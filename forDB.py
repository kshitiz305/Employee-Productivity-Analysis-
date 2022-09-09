import sqlite3
from sqlite3 import Error
from tkinter import messagebox
import tkinter

db_path = r'SampleData.db'

# This code will insert record into DTE,STAFFIT and Calender tables
def insert_record(dfs, table_name):
    try:
        conn = sqlite3.connect(db_path)
        dfs.to_sql(table_name, conn)
        # commit the changes to db
        conn.commit()
        # close the connection
        conn.close()
        return table_name
    except Error as e:
        print(e)
if __name__ == '__main__':
    root = tkinter.Tk()
    root.withdraw()  # use to hide tkinter window
    messagebox.showerror("Error", "Not to be executed as standalone file....")
