import pyodbc
import os
import json
import re
import requests
from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

@app.route('/api/print_table_columns', methods=['GET'])
def api_print_table_columns():
    tablename = request.args.get('tablename')
    print_table_columns(tablename)
    return jsonify({"message": "Table columns printed."})

@app.route('/api/fetch_rows', methods=['GET'])
def api_fetch_rows():
    tablename = request.args.get('tablename')
    fetch_rows(tablename)
    return jsonify({"message": "Rows fetched."})

@app.route('/api/fetch', methods=['GET'])
def fetch_data():
    response = requests.get('http://localhost:5000/convert')
    data = response.json()
    return jsonify(data)

if __name__ == '__main__':
    app.run(port=5001)

# List all MS-Access drivers available
    msa_drivers = [x for x in pyodbc.drivers() if 'ACCESS' in x.upper()]
print(f'MS-Access drivers: \n{msa_drivers}')

# Function to get database connection
def get_dbconn(file, password=None):
    pyodbc.pooling = False
    # Check if there is any MS-Access driver available
    if msa_drivers:
        # Use the first available MS-Access driver
        driver = msa_drivers[0]
    else:
        # If no MS-Access drivers are available, raise an error
        raise Exception("No MS-Access drivers found. Please install the appropriate driver.")
    
    # Create the connection string using the correct file path
    dbdsn = f'Driver={{{driver}}};DBQ={file};'
    if password:
        dbdsn += f'PWD={password};'
    # Connect to the database
    return pyodbc.connect(dbdsn)

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Define relative paths
db_path = os.path.join(current_dir, 'Hackathon.accde')

# Attempt to connect to the database using the correct file path
try:
    dbconn = get_dbconn(db_path)
    cursor = dbconn.cursor()
    # Print the names of all tables in the database
    for table_info in cursor.tables(tableType='TABLE'):
        print(f'Table: {table_info.table_name}')
except Exception as e:
    print(f"An error occurred: {e}")

# Function to print column names for a given table
def print_table_columns(tablename):
    print(f'---- Table: {tablename}')
    cursor = dbconn.cursor()
    cursor.execute(f'SELECT * FROM [{tablename}]')
    for col in cursor.description:
        print(f'\tcol: {col[0]}')
    cursor.close()

# Function to fetch rows from a given table with ID greater than or equal to 1
def fetch_rows(tablename):
    sql = f'SELECT * FROM [{tablename}] WHERE ID >= ?'
    cursor = dbconn.cursor()
    cursor.execute(sql, (1,))
    rows = cursor.fetchall()
    cursor.close()
    return rows  # Return the rows as a list

# Function to insert a new row with empty values
def insert_empty_row(tablename):
    sql = f'INSERT INTO [{tablename}] (Product, Amount) VALUES (?, ?)'
    sql_data = ('', 0)  # Insert empty string for Product and 0 for Amount
    cursor = dbconn.cursor()
    cursor.execute(sql, sql_data)
    dbconn.commit()
    cursor.close()


# Function to update only empty rows in the table with data from JSON
def update_empty_rows_from_json(tablename, data):

    # Extract the relevant data from 'extracted_data'
    extracted_data = data.get('extracted_data', {})
    print("Extracted data:", extracted_data)
    
        # Extract rows with alpha characters and currency
    entries = []
    for product, amount in extracted_data.items():
        if re.match(r'^[a-zA-Z\s*]+$', product) and re.match(r'^\$\d+\.\d{2}$', amount):
            entries.append({'Product': product, 'Amount': amount})
    print("Entries to update:", entries)

        # Only proceed if there are valid entries
    if entries:

    
        # Fetch the IDs of the newly inserted empty rows
        try:
            cursor.execute(f"SELECT ID FROM [{tablename}] WHERE Product = '' OR Product IS NULL ORDER BY ID")
            empty_row_ids = [row.ID for row in cursor.fetchall()]
            print("Empty row IDs:", empty_row_ids)
        except Exception as e:
            print(f"Error fetching empty row IDs: {e}")
            return
    # Fetch the IDs of the newly inserted empty rows
    try:
        cursor.execute(f"SELECT ID FROM [{tablename}] WHERE Product = '' OR Product IS NULL ORDER BY ID")
        empty_row_ids = [row.ID for row in cursor.fetchall()]
        print("Empty row IDs:", empty_row_ids)
    except Exception as e:
        print(f"Error fetching empty row IDs: {e}")
        return
    
        # Update the empty rows with the extracted data
        for entry, empty_row_id in zip(entries, empty_row_ids):
            try:
                sql = f'UPDATE [{tablename}] SET Product = ?, Amount = ? WHERE ID = ?'
                sql_data = (entry['Product'], entry['Amount'], empty_row_id)
                print(f"Executing SQL: {sql} with data: {sql_data}")
                cursor.execute(sql, sql_data)
                dbconn.commit()
                print(f"Updated empty row with ID {empty_row_id} with Product: {entry['Product']} and Amount: {entry['Amount']}")
            except Exception as e:
                print(f"Error updating row: {e}")
        cursor.close()
    else:
        print("No valid entries found in the JSON data.")


@app.route('/api/insert_empty_row', methods=['POST'])
def api_insert_empty_row():
    tablename = request.json.get('tablename')
    insert_empty_row(tablename)
    return jsonify({"message": "Empty row inserted."})

@app.route('/api/update_empty_rows_from_json', methods=['POST'])
def api_update_empty_rows_from_json():
    tablename = request.json.get('tablename')
    data = request.json.get('data')
    update_empty_rows_from_json(tablename, data)
    return jsonify({"message": "Empty rows updated from JSON."})

@app.route('/api/update_and_fetch', methods=['POST'])
def api_update_and_fetch():
    tablename = request.json.get('tablename')
    data = request.json.get('data')
    update_empty_rows_from_json(tablename, data)
    
    # Fetch rows and return them as JSON
rows = fetch_rows('OCR TEST')
""" return jsonify(rows) """

# Call the functions
if __name__ == '__main__':
# Fetch rows and print them all at once
    rows = fetch_rows('OCR TEST')
for row in rows:
    print(row.ID, row.Product, row.Amount)

# Close the database connection
dbconn.close()
