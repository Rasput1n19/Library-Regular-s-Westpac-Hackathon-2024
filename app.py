import pyodbc
import os
import json
import re
from flask_cors import CORS
from flask import Flask, request, jsonify
from PIL import Image
import pytesseract
import os
from PIL import Image
app = Flask(__name__)
CORS(app)

# Ensure the correct path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update this path if necessary

def extract_text_from_image(image_path):
    try:
        with Image.open(image_path) as img:
            text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        return str(e)



@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        #file_path = os.path.join('\\tmp', file.filename)
        file_path = file.filename
        file.save(file_path)
        text = extract_text_from_image(file_path)
        #text = text
        os.remove(file_path)
        return jsonify({'text': text})
if __name__ == '__main__':
    app.run(port=5000)


def extract_text_from_image(image_path):
    try:
        # Open an image file
        with Image.open(r"C:\Users\Ben Lange\Desktop\my-app\src\Receipt 1.jpg") as img:
            # Use pytesseract to extract text
            text = pytesseract.image_to_string(img)

        # Process the text into key-value pairs
        data = process_text_to_json(text)

        return data
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def process_text_to_json(raw_text):
    lines = raw_text.split('\n')
    data = {}
    for line in lines:
        if line.strip():
            # Assuming each line contains "item name - $price"
            parts = line.split('$')
            if len(parts) == 2:
                item = parts[0].strip()
                price = '$' + parts[1].strip()
                data[item] = price
    return data


def save_to_json(data, json_path):
    try:
        with open(json_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        print(f"Data successfully saved to {json_path}")
    except Exception as e:
        print(f"An error occurred while saving to JSON: {e}")


def print_json_file(json_path):
    try:
        with open(json_path, 'r') as json_file:
            data = json.load(json_file)
            print(json.dumps(data, indent=4))
    except Exception as e:
        print(f"An error occurred while reading the JSON file: {e}")


# Example usage
""" image_path = 'PXL_20240704_072217636.jpg'  # Replace with your image path
extracted_data = extract_text_from_image(image_path)
if extracted_data:
    response = {
        "filename": os.path.basename(image_path),
        "extracted_data": extracted_data
    }
    json_path = 'extracted_data.json'  # The path where the JSON file will be saved
    save_to_json(response, json_path)
    # Print the contents of the JSON file
    print_json_file(json_path) """

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
json_file_path = os.path.join(current_dir, 'Receipt.json')

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
    for row in cursor.fetchall():
        print(row.ID, row.Product, row.Amount)
    cursor.close()

# Function to insert a new row with empty values
def insert_empty_row(tablename):
    sql = f'INSERT INTO [{tablename}] (Product, Amount) VALUES (?, ?)'
    sql_data = ('', 0)  # Insert empty string for Product and 0 for Amount
    cursor = dbconn.cursor()
    cursor.execute(sql, sql_data)
    dbconn.commit()
    cursor.close()

# Function to update only empty rows in the table with data from JSON file
def update_empty_rows_from_json(tablename, json_file):
# Load the JSON file
    f = open("data.json", 'x')
    f.close()
    json_file = 'data.json'  
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)
        print("JSON data loaded successfully:", data)
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        
    return
tablename = 'OCR TEST'
    # Open the JSON file
    # Load the JSON file
 # The path to your JSON file
# ...

# Function to update only empty rows in the table with data from JSON file
def update_empty_rows_from_json(tablename, json_file):
    # Load the JSON file
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)
        print("JSON data loaded successfully:", data)
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return
    
    # Extract rows with alpha characters and currency
    entries = []
    for product, amount in data.get('extracted_data', {}).items():
        if re.match(r'^[a-zA-Z\s*]+$', product) and re.match(r'^\$\d+\.\d{2}$', amount):
            entries.append({'Product': product, 'Amount': amount})
    print("Entries to update:", entries)
    
    # Add the necessary number of empty rows to the database
    cursor = dbconn.cursor()
    try:
        for _ in range(len(entries)):
            cursor.execute(f"INSERT INTO [{tablename}] (Product, Amount) VALUES ('', 0)")
        dbconn.commit()
        print(f"Inserted {len(entries)} empty rows.")
    except Exception as e:
        print(f"Error inserting empty rows: {e}")
    
    # Fetch the IDs of the newly inserted empty rows
    try:
        cursor.execute(f"SELECT ID FROM [{tablename}] WHERE Product = '' OR Product IS NULL ORDER BY ID")
        empty_row_ids = [row.ID for row in cursor.fetchall()]
        print("Empty row IDs:", empty_row_ids)
    except Exception as e:
        print(f"Error fetching empty row IDs: {e}")

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

# Call the functions
update_empty_rows_from_json('OCR TEST',  json_file_path)
print_table_columns('OCR TEST')
fetch_rows('OCR TEST')
insert_empty_row('OCR TEST')

# Close the database connection
dbconn.close()