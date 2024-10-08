import sqlite3
import streamlit as st
import pandas as pd



# ============================================= Display functions ==========================================

# Function to connect to the SQLite database and fetch table data
def load_data_from_db(db_name, table_name):
    conn = sqlite3.connect(db_name)
    query = f'SELECT * FROM {table_name}'
    df = pd.read_sql(query, conn)
    conn.close()
    return df






# ==================================== Table data operations functions ======================================


# Function to create a connection to the SQLite database
def create_connection(db_file):
    conn = sqlite3.connect(db_file)
    return conn

# Function to fetch table names
def get_table_names_dataops(conn):
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    tables = pd.read_sql_query(query, conn)
    return tables['name'].tolist()

# Function to fetch column names and their types for a given table
def get_columns_and_types(conn, table_name):
    query = f"PRAGMA table_info({table_name});"
    columns_info = pd.read_sql_query(query, conn)
    return columns_info[['name', 'type']]

# Function to fetch data from a specified table
def fetch_table_data(conn, table_name):
    query = f"SELECT * FROM {table_name};"
    return pd.read_sql_query(query, conn)

# Function to execute a SQL command with parameters
def execute_query(conn, query, params=None):
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    conn.commit()


# ==================================== Table operations functions ===================================



# Function to create a SQLite database and table
def create_table(table_name, columns, primary_keys, foreign_keys):
    conn = sqlite3.connect('admin.db')
    c = conn.cursor()

    # Construct column definitions
    column_definitions = []
    for col in columns:
        col_def = f"{col['name']} {col['type']}"
        column_definitions.append(col_def)

    # Add primary key constraint
    if primary_keys:
        primary_key_def = f"PRIMARY KEY ({', '.join(primary_keys)})"
        column_definitions.append(primary_key_def)

    # Add foreign key constraints
    for fk in foreign_keys:
        fk_def = f"FOREIGN KEY ({fk['column']}) REFERENCES {fk['ref_table']}({fk['ref_column']})"
        column_definitions.append(fk_def)

    # Create the table SQL
    create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ("
    create_table_query += ", ".join(column_definitions)
    create_table_query += ");"

    # Execute table creation
    c.execute(create_table_query)
    conn.commit()
    conn.close()

# Function to delete a table
def delete_table(table_name):
    conn = sqlite3.connect('admin.db')
    c = conn.cursor()
    c.execute(f"DROP TABLE IF EXISTS {table_name};")
    conn.commit()
    conn.close()

# Function to insert a column
def insert_column(table_name, column_name, column_type):
    conn = sqlite3.connect('admin.db')
    c = conn.cursor()
    c.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};")
    conn.commit()
    conn.close()

# Function to remove a column (SQLite doesn't support DROP COLUMN directly)
def remove_column(table_name, column_name):
    conn = sqlite3.connect('admin.db')
    c = conn.cursor()
    
    # Fetch all columns in the table
    c.execute(f"PRAGMA table_info({table_name});")
    columns = c.fetchall()
    
    # Create a new table without the column to be removed
    new_columns = [col[1] for col in columns if col[1] != column_name]
    
    # Create new table
    new_table_name = f"{table_name}_temp"
    column_definitions = ", ".join([f"{col} TEXT" for col in new_columns])
    c.execute(f"CREATE TABLE {new_table_name} ({column_definitions});")
    
    # Copy data to the new table
    c.execute(f"INSERT INTO {new_table_name} ({', '.join(new_columns)}) SELECT {', '.join(new_columns)} FROM {table_name};")
    
    # Drop the old table and rename the new table
    c.execute(f"DROP TABLE {table_name};")
    c.execute(f"ALTER TABLE {new_table_name} RENAME TO {table_name};")
    
    conn.commit()
    conn.close()
