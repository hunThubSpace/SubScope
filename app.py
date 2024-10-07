from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# Function to connect to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('scopes.db')
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

# Basic Query String Construction Helper
def build_query(filters, table_name):
    query = f"SELECT * FROM {table_name} WHERE "
    conditions = []
    parameters = []

    for column, value in filters.items():
        if value:
            conditions.append(f"{column} LIKE ?")
            parameters.append(f"%{value}%")

    if conditions:
        query += " AND ".join(conditions)
    else:
        query = query.replace(" WHERE ", "")  # No filtering if no conditions

    return query, parameters

@app.route('/')
def index():
    conn = get_db_connection()

    # Fetch all data for rendering on page load
    programs = conn.execute('SELECT * FROM programs').fetchall()
    domains = conn.execute('SELECT * FROM domains').fetchall()
    subdomains = conn.execute('SELECT * FROM subdomains').fetchall()
    urls = conn.execute('SELECT * FROM urls').fetchall()
    cidrs = conn.execute('SELECT * FROM cidrs').fetchall()

    # Calculate overview data
    programs_count = len(programs)
    domains_count = len(domains)
    subdomains_count = len(subdomains)
    urls_count = len(urls)
    cidrs_count = len(cidrs)

    return render_template('index.html', 
                           programs=programs, domains=domains, subdomains=subdomains, 
                           urls=urls, cidrs=cidrs,
                           programs_count=programs_count, domains_count=domains_count, 
                           subdomains_count=subdomains_count, urls_count=urls_count, 
                           cidrs_count=cidrs_count)

if __name__ == '__main__':
    app.run(debug=True)
