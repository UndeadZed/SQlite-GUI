import streamlit as st
import sqlite3
import pandas as pd
from utils import *

# Main app function
def data_ops_page():
    # Connect to SQLite database
    conn = create_connection('admin.db')

    # Sidebar for operations
    st.sidebar.title("Database Operations")
    operation = st.sidebar.selectbox("Choose an operation", ["Add Row", "Edit Row", "Delete Row"])

    # Get table names
    table_names = get_table_names(conn)
    table_name = st.sidebar.selectbox("Select Table", table_names)

    if operation == "Add Row":
        st.subheader(f"Add a new row to {table_name}")
        columns = get_columns_and_types(conn, table_name)
        form = st.form(key='add_form')
        
        # Create input fields for each column
        inputs = {}
        for _, row in columns.iterrows():
            col_name = row['name']
            col_type = row['type']
            if col_type.lower() == "text":
                inputs[col_name] = form.text_input(col_name)
            elif col_type.lower() in ["integer", "real"]:
                inputs[col_name] = form.number_input(col_name, format="%d" if col_type.lower() == "integer" else "%f")
        
        submit_button = form.form_submit_button("Add Row")
        if submit_button:
            insert_query = f"INSERT INTO {table_name} ({', '.join(inputs.keys())}) VALUES ({', '.join(['?' for _ in inputs])})"
            execute_query(conn, insert_query, tuple(inputs.values()))
            st.success("Row added successfully!")

    elif operation == "Edit Row":
        st.subheader(f"Edit a row in {table_name}")
        data = fetch_table_data(conn, table_name)
        
        # Use a select box to choose a row to edit
        row_to_edit = st.selectbox("Select row to edit", data.index)
        
        # Create a form for editing the selected row
        form = st.form(key='edit_form')
        original_row = data.loc[row_to_edit]
        edited_inputs = {}
        
        columns = get_columns_and_types(conn, table_name)
        for _, row in columns.iterrows():
            col_name = row['name']
            col_type = row['type']
            if col_type.lower() == "text":
                edited_inputs[col_name] = form.text_input(col_name, value=original_row[col_name])
            elif col_type.lower() in ["integer", "real"]:
                edited_inputs[col_name] = form.number_input(col_name, value=original_row[col_name], 
                                                             format="%d" if col_type.lower() == "integer" else "%f")
        
        submit_button = form.form_submit_button("Save Changes")
        if submit_button:
            # Create a list to hold the new values, using original if the input is empty
            new_values = [
                edited_inputs[col] if edited_inputs[col] else original_row[col]
                for col in original_row.index
            ]
            update_query = f"UPDATE {table_name} SET {', '.join([f'{col} = ?' for col in data.columns])} WHERE rowid = ?"
            execute_query(conn, update_query, (*new_values, row_to_edit + 1))  # rowid is 1-based
            st.success("Row updated successfully!")

    elif operation == "Delete Row":
        st.subheader(f"Delete a row from {table_name}")
        data = fetch_table_data(conn, table_name)
        row_to_delete = st.selectbox("Select row to delete", data.index)
        
        if st.button("Delete Row"):
            delete_query = f"DELETE FROM {table_name} WHERE rowid = ?"
            execute_query(conn, delete_query, (row_to_delete + 1 ,))  # rowid is 1-based
            st.success("Row deleted successfully!")

    # Close the database connection
    conn.close()

if __name__ == "__main__":
    data_ops_page()
