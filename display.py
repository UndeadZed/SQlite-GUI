import sqlite3
import pandas as pd
import streamlit as st
from utils import *


# ---------------------------------------------- Data Operations ---------------------------------------------
def Data_ops_page():
    # Connect to SQLite database
    conn = create_connection('admin.db')

    # Sidebar for operations
    st.sidebar.title("Database Operations")
    operation = st.sidebar.selectbox("Choose an operation", ["Add Row", "Edit Row", "Delete Row"])

    # Get table names
    table_names = get_table_names_dataops(conn)
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


# ---------------------------------------------- Table Operations --------------------------------------------

def Table_ops_page():
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


# --------------------------------------------- The table viewer ---------------------------------------------

# Function to fetch table names
def get_table_names(db_file):
    conn = sqlite3.connect(db_file)
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    tables = pd.read_sql_query(query, conn)
    conn.close()
    return tables['name'].tolist()

def Table_viewer_page():

    # Streamlit app starts here
    st.title("SQlite Data viewer")


    # Input: database and table details
    db_name = "admin.db"
    table_names = get_table_names(db_name)
    table_name = st.sidebar.selectbox("Select Table", table_names)


    # Button to load data
    if st.button("Load Data"):
        try:
            # Load data from database
            data = load_data_from_db(db_name, table_name)
            st.success(f"Successfully loaded data from the '{table_name}' table.")
            
            # Display the data in the app
            st.write("### Data Preview:")
            st.dataframe(data)
            
            # Option to download data as CSV
            csv = data.to_csv(index=False)
            st.download_button("Download data as CSV", csv, f"{table_name}.csv", "text/csv")

        except Exception as e:
            st.error(f"Error loading data: {e}")

    # Option to display raw SQL query results (if needed)
    st.write("You can modify the table name or database name in the input fields to load other tables.")



def app():
    page = st.sidebar.selectbox('Pages:', ('Table Viewer', 'Table Operations', 'Data Operations'))
    if page == 'Table Viewer':
        Table_viewer_page()
    elif page == 'Table Operations':
        Table_ops_page()
    else:
        Data_ops_page()



if __name__ == "__main__":
    app()