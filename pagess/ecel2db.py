import streamlit as st
import pandas as pd
import sqlite3

# Function to map pandas dtypes to SQLite types
def map_dtype(dtype):
    if pd.api.types.is_numeric_dtype(dtype):
        return "REAL"
    elif pd.api.types.is_string_dtype(dtype):
        return "TEXT"
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        return "TEXT"  # Dates as text (can be converted back to datetime later)
    else:
        return "TEXT"

# Function to check if a table exists in SQLite
def check_table_exists(conn, table_name):
    query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?;"
    result = conn.execute(query, (table_name,)).fetchone()
    return result is not None

# Function to update existing rows or insert new rows based on the primary key
def upsert_data(conn, df, table_name, primary_key):
    # Fetch the existing data in the table
    existing_data = pd.read_sql(f"SELECT * FROM {table_name}", conn)

    for index, row in df.iterrows():
        # Check if the primary key value exists in the existing data
        primary_key_value = row[primary_key]
        existing_row = existing_data[existing_data[primary_key] == primary_key_value]

        if not existing_row.empty:
            # Update the row if it exists and data differs
            update_required = False
            for col in df.columns:
                if row[col] != existing_row.iloc[0][col]:
                    update_required = True
                    break

            if update_required:
                update_query = f"UPDATE {table_name} SET {', '.join([f'{col}=?' for col in df.columns])} WHERE {primary_key}=?"
                conn.execute(update_query, tuple(row) + (primary_key_value,))
                st.write(f"Row with {primary_key}={primary_key_value} updated.")
        else:
            # Insert the row if it doesn't exist
            insert_query = f"INSERT INTO {table_name} ({', '.join(df.columns)}) VALUES ({', '.join('?' * len(df.columns))})"
            conn.execute(insert_query, tuple(row))
            st.write(f"Row with {primary_key}={primary_key_value} inserted.")

# Function to create a new table based on the dataframe and primary key selection
def create_table_from_df(conn, df, table_name, primary_key):
    # Build the SQL column definitions
    columns = [f"{col} {map_dtype(df[col].dtype)}" for col in df.columns]
    
    # Define the primary key column
    if primary_key in df.columns:
        columns = [f"{col} PRIMARY KEY" if col == primary_key else col for col in columns]
    
    # Join the column definitions into a CREATE TABLE statement
    columns_def = ", ".join(columns)
    create_table_query = f"CREATE TABLE {table_name} ({columns_def});"
    
    # Execute the query
    conn.execute(create_table_query)
    st.success(f"Table '{table_name}' created successfully with primary key '{primary_key}'.")

# Main app function
def main():
    st.title("Excel to SQLite Database")

    # File uploader
    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

    if uploaded_file:
        # Read the uploaded Excel file
        df = pd.read_excel(uploaded_file)

        # Display the uploaded data
        st.write("Preview of uploaded data:")
        st.dataframe(df)

        # Connect to the SQLite database
        db_file = "admin.db"
        conn = sqlite3.connect(db_file)

        # Get the list of tables in the database
        table_names = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
        
        # Check if there's a matching table based on column names
        matching_table = None
        for table_name in table_names['name']:
            existing_columns = [col[1] for col in conn.execute(f"PRAGMA table_info({table_name});")]
            new_columns = df.columns.tolist()

            if set(existing_columns) == set(new_columns):
                matching_table = table_name
                break

        if matching_table:
            # If a matching table is found, ask for the primary key to use for updates
            st.write(f"Table '{matching_table}' matches the columns of the Excel file.")
            primary_key = st.selectbox("Select the primary key for the existing table:", df.columns)

            if st.button("Update Table"):
                upsert_data(conn, df, matching_table, primary_key)
        else:
            # If no matching table, ask the user to enter a table name and choose a primary key
            st.write("No matching table found. You can create a new table.")
            table_name = st.text_input("Enter the name for the new table:")

            if table_name.strip() == "":
                st.warning("Please enter a valid table name.")
            else:
                # Ask the user to choose a primary key from the dataframe columns
                primary_key = st.selectbox("Select the primary key for the new table:", df.columns)
                
                # Create the new table and insert the data
                if st.button("Create Table and Insert Data"):
                    create_table_from_df(conn, df, table_name, primary_key)
                    upsert_data(conn, df, table_name, primary_key)

        # Commit changes and close the connection
        conn.commit()
        conn.close()

if __name__ == "__main__":
    main()
