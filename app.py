from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import re
import uuid

app = Flask(__name__)

# Function to set up database
def setup_database():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patient_data (
        patient_id TEXT PRIMARY KEY,
        name TEXT,
        age INTEGER,
        diagnosis TEXT,
        medications TEXT,
        recommendations TEXT
    )
    """)
    conn.commit()
    conn.close()

setup_database()

# Function to extract patient data
def extract_data_from_paragraph(report):
    patterns = {
        'name': r"Name[:\-]?\s*([A-Za-z\s]+)",
        'age': r"Age[:\-]?\s*(\d+)",
        'diagnosis': r"Diagnosis[:\-]?\s*([A-Za-z\s,]+)",
        'medications': r"Medications[:\-]?\s*([A-Za-z\s,]+)",
        'recommendations': r"Recommendations[:\-]?\s*(.+)"
    }

    extracted_data = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, report, re.IGNORECASE)
        extracted_data[key] = match.group(1).strip() if match else "N/A"

    extracted_data['patient_id'] = str(uuid.uuid4())
    return extracted_data

# Route for the homepage
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle form submission
@app.route('/submit', methods=['POST'])
def submit():
    report = request.form['report']
    data = extract_data_from_paragraph(report)
    
    # Store data in the database
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO patient_data (patient_id, name, age, diagnosis, medications, recommendations)
    VALUES (:patient_id, :name, :age, :diagnosis, :medications, :recommendations)
    """, data)
    conn.commit()
    conn.close()

    return redirect(url_for('results'))

# Route to display results
@app.route('/results')
def results():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patient_data")
    rows = cursor.fetchall()
    conn.close()

    return render_template('results.html', rows=rows)

if __name__ == "__main__":
    app.run(debug=True)
