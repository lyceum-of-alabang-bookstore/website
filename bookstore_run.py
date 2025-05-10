from flask import Flask, render_template, jsonify, request, redirect, url_for, Response, flash
import sqlite3
import os

app = Flask(__name__)

app.secret_key = 'a7e4c1c9023b45db92d7b7d47375f91f2092f7a46c2f4b8c2834fbc92eeb23d1'


USERNAME = 'Administrator'
PASSWORD = 'loabookstoreadmin2003'

def check_auth(username, password):
    return username == USERNAME and password == PASSWORD

def authenticate():
    return Response(
        'Access denied.\n'
        'You need to login with proper credentials.', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    decorated.__name__ = f.__name__
    return decorated


# Use an absolute path for the database file
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'items.db')

@app.route('/api/items')
def api_items():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, category, price, stock_status FROM items")
        items = cursor.fetchall()
    return jsonify([
        {'id': row[0], 'name': row[1], 'category': row[2], 'price': row[3], 'stock_status': row[4]}
        for row in items
    ])

@app.route('/api/in-stock')
def api_in_stock():
    # Now include 'stock_status' in the select statement
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, category, price, stock_status FROM items WHERE stock_status = 'In-stock'")
        items = cursor.fetchall()
    return jsonify([
        {'id': row[0], 'name': row[1], 'category': row[2], 'price': row[3], 'stock_status': row[4]}
        for row in items
    ])

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/category.html')
def category():
    return render_template('category.html')

@app.route('/all_items.html')
def all_items():
    return render_template('all_items.html')

@app.route('/in_stock.html')
def in_stock():
    return render_template('in_stock.html')

@app.route('/order_summary.html')
def order_summary():
    return render_template('order_summary.html')

@app.route('/admin')
@requires_auth
def admin():
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items")
        rows = cursor.fetchall()
    return render_template('admin.html', items=rows)

@app.route('/admin/edit/<int:item_id>', methods=['POST'])
def admin_edit(item_id):
    name = request.form['name']
    category = request.form['category']
    price = request.form['price']
    stock_status = request.form['stock_status']

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE items SET name = ?, category = ?, price = ?, stock_status = ? WHERE id = ?",
                       (name, category, price, stock_status, item_id))
        conn.commit()
    flash('Item updated successfully.')
    return redirect(url_for('admin'))


@app.route('/admin/add', methods=['POST'])
def admin_add():
    name = request.form['name']
    category = request.form['category']
    price = request.form['price']
    stock_status = request.form['stock_status']

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO items (name, category, price, stock_status) VALUES (?, ?, ?, ?)",
                       (name, category, price, stock_status))
        conn.commit()
    flash('Item added successfully.')
    return redirect(url_for('admin'))

@app.route('/admin/remove/<int:item_id>', methods=['POST'])
def admin_remove(item_id):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
        conn.commit()

    flash('Item deleted successfully.')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))  # Use PORT env var if available
    app.run(host='0.0.0.0', port=port)

