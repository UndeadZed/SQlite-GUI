import streamlit as st
import sqlite3
from utils import *

def table_ops_page():
    # Streamlit App
    st.title("Dynamic Database and Table Management")

    # Sidebar for operations
    operation = st.sidebar.selectbox("Choose Operation", ["Create Table", "Delete Table", "Insert Column", "Remove Column"])

    if operation == "Create Table":
        # Input: Table name
        table_name = st.text_input("Enter Table Name")

        # Input: Number of columns
        num_columns = st.number_input("Enter Number of Columns", min_value=1, max_value=20, value=1)

        # Input: Column definitions
        columns = []
        for i in range(num_columns):
            col_name = st.text_input(f"Column {i+1} Name", key=f"name_{i}")
            col_type = st.selectbox(f"Column {i+1} Type", ["TEXT", "INTEGER", "REAL", "BLOB"], key=f"type_{i}")
            columns.append({"name": col_name, "type": col_type})

        # Primary Key Input
        st.subheader("Primary Key")
        primary_keys = st.multiselect("Select Primary Key Column(s)", [col['name'] for col in columns if col['name']])

        # Foreign Key Input
        st.subheader("Foreign Key Constraints")
        num_fks = st.number_input("Enter Number of Foreign Keys", min_value=0, max_value=num_columns, value=0)

        foreign_keys = []
        for i in range(num_fks):
            fk_column = st.selectbox(f"Foreign Key Column {i+1}", [col['name'] for col in columns if col['name']], key=f"fk_col_{i}")
            ref_table = st.text_input(f"Referenced Table {i+1}", key=f"ref_table_{i}")
            ref_column = st.text_input(f"Referenced Column {i+1}", key=f"ref_col_{i}")
            foreign_keys.append({"column": fk_column, "ref_table": ref_table, "ref_column": ref_column})

        # Button to create the table
        if st.button("Create Table"):
            if table_name and all(col['name'] for col in columns):
                create_table(table_name, columns, primary_keys, foreign_keys)
                st.success(f"Table '{table_name}' created successfully with keys!")
            else:
                st.error("Please provide valid table name and column details.")

    elif operation == "Delete Table":
        table_name = st.text_input("Enter Table Name to Delete")
        if st.button("Delete Table"):
            if table_name:
                delete_table(table_name)
                st.success(f"Table '{table_name}' deleted successfully.")
            else:
                st.error("Please provide a valid table name.")

    elif operation == "Insert Column":
        table_name = st.text_input("Enter Table Name to Insert Column")
        col_name = st.text_input("New Column Name")
        col_type = st.selectbox("New Column Type", ["TEXT", "INTEGER", "REAL", "BLOB"])
        if st.button("Insert Column"):
            if table_name and col_name:
                insert_column(table_name, col_name, col_type)
                st.success(f"Column '{col_name}' added to table '{table_name}'.")
            else:
                st.error("Please provide valid table name and column name.")

    elif operation == "Remove Column":
        table_name = st.text_input("Enter Table Name to Remove Column")
        col_name = st.text_input("Column Name to Remove")
        if st.button("Remove Column"):
            if table_name and col_name:
                remove_column(table_name, col_name)
                st.success(f"Column '{col_name}' removed from table '{table_name}'.")
            else:
                st.error("Please provide valid table name and column name.")


if __name__ == "__main__":
    table_ops_page()