from flask import Flask, request, redirect, render_template_string
import sqlite3
import string
import random

app = Flask(__name__)

# Database setup
DATABASE = 'urls.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS urls (short TEXT, original TEXT)')
        conn.commit()

def insert_url_mapping(short, original):
    with get_db_connection() as conn:
        conn.execute('INSERT INTO urls (short, original) VALUES (?, ?)', (short, original))
        conn.commit()

def get_original_url(short):
    with get_db_connection() as conn:
        original = conn.execute('SELECT original FROM urls WHERE short = ?', (short,)).fetchone()
        if original:
            return original['original']
        return None

# Generate a short identifier
def generate_short_id(num_chars=6):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(num_chars))

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        original_url = request.form['original_url']
        short_id = generate_short_id()
        insert_url_mapping(short_id, original_url)
        return render_template_string('Short URL is: {{short_url}}', short_url=request.host_url + short_id)
    return '''
        <form method="post">
            Original URL: <input type="text" name="original_url"><br>
            <input type="submit" value="Shorten">
        </form>
    '''

@app.route('/<short_id>')
def redirect_to_original(short_id):
    original_url = get_original_url(short_id)
    if original_url:
        return redirect(original_url)
    return 'URL not found', 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
