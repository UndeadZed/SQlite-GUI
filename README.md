
# SQlite-GUI database creator/editor streamlit app

## Overview
A simple streamlit app made to allow for creating databases through a GUI without having to go through the hassle of writing the SQLite queries yourself.

## Motivation
The motivation behind this initiative stemmed from the need to create an easy way to make databases without writing the queries yourself which can be repetitive and time consuming in some cases.

## Requirements
The requirements are that you have python 3.9 or higher installed and install all the libraries listed in the requirements.txt file 

## How it Works:

first you need to write the following commands in the terminal

` streamlit run app.py `

### there are basically 4 pages in this app which are all linked to database creation and managemnt

#### 1- Table Viewer: a page which uses pandas and streamlit to load the data of the table into a dataframe and display it effectively showing the table
#### 2- Table Operations: a page for any table operations that you might need which are basically creating and deleting tables as well as inserting and removing columns and rows
#### 3- Data Operations: a page which edits the data inside the table effectively deleting or editing a row
#### 4- Database Assistant: a page which uses a llama based llm (hasn't been decided yet probably code llama tho) to allow for database operation execution via natural language by conversing with the database Assistant

## Additional notes:
1. We are currently in the process of developing a Google Colab notebook utilizing this repository, which will be made available shortly. 
2. The local version of this application will implement alternative APIs for the development of the database assistant, deliberately omitting the use of local LLMs to conserve resources.
3. Conversely, the Colab version will incorporate the LLAMA 3.1 and LLAMA 2 local LLMs, which are presently under development.
4. It is important to note that the existing codebase requires significant refinement; thus, following the completion of the Colab notebook, our primary focus will shift toward streamlining and enhancing the overall quality of the code.


