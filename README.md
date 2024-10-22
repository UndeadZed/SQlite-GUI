
# SQlite-GUI database creator/editor streamlit app

## Overview
A simple streamlit app made to allow for creating databases through a GUI without having to go through the hassle of writing the SQLite queries yourself.

## Motivation
The motivation behind this initiative stemmed from the need to create an easy way to make databases without writing the queries yourself which can be repetitive and time consuming in some cases.

## Requirements
The requirements are that you have python 3.9 or higher installed and install all the libraries listed in the requirements.txt file.

## How it Works

### there are basically 4 pages in this app which are all linked to database creation and managemnt

#### 1- Table Viewer: a page which uses pandas and streamlit to load the data of the table into a dataframe and display it effectively showing the table
#### 2- Table Operations: a page for any table operations that you might need which are basically creating and deleting tables as well as inserting and removing columns and rows
#### 3- Data Operations: a page which edits the data inside the table effectively deleting or editing a row
#### 4- Database Assistant: a page which uses a llama based llm (hasn't been decided yet probably code llama tho) to allow for database operation execution via natural language by conversing with the database Assistant

