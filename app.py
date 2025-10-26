from flask import Flask, render_template, request, redirect, url_for
import sqlite3
app = Flask(__name__)
def init_db():
    conn = sqlite3.connect('quotes.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS quotes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    quote TEXT NOT NULL
      )''')
    conn.commit()
    conn.close()
def get_all_quotes():
    conn = sqlite3.connect('quotes.db')
    c = conn.cursor()
    c.execute("SELECT id, quote FROM quotes")
    quotes = c.fetchall()
    conn.close()
    return quotes
def add_quote_to_db(quote):
    conn = sqlite3.connect('quotes.db')
    c = conn.cursor()
    c.execute("INSERT INTO quotes (quote) VALUES (?)", (quote,))
    conn.commit()
    conn.close()
def delete_quote_from_db(quote_id):
    conn = sqlite3.connect('quotes.db')
    c = conn.cursor()
    c.execute("DELETE FROM quotes WHERE id = ?", (quote_id,))
    conn.commit()
    conn.close()
@app.route('/')
def index():
    quotes = get_all_quotes()
    return render_template('index.html', quotes=quotes)
@app.route('/add', methods=['GET', 'POST'])
def add_quote():
    if request.method == 'POST':
        quote = request.form['quote']
        if quote.strip():
            add_quote_to_db(quote.strip())
        return redirect(url_for('index'))
    return render_template('add_quote.html')

@app.route('/delete/<int:quote_id>')
def delete_quote(quote_id):
    delete_quote_from_db(quote_id)
    return redirect(url_for('index'))
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
