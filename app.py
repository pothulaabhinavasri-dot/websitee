from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
import json
import os
import uuid  # Moved import to the top with others

app = Flask(__name__)

# --- 1. CONFIGURATION & DATA SETUP ---

# Ensure data directory exists for order history
# Note: Netlify functions are "read-only". 
# For a real project, you'd use a database like MongoDB or Firebase later.
if not os.path.exists('/tmp/data'):
    os.makedirs('/tmp/data')

STORES = [
    {"id": 1, "name": "Paradise Biryani", "rating": "4.8", "desc": "World Famous"},
    {"id": 2, "name": "Kritunga Restaurant", "rating": "4.5", "desc": "Rayalaseema Style"},
    {"id": 3, "name": "Trends Restaurant", "rating": "4.2", "desc": "North Indian"},
    {"id": 4, "name": "Red Bucket", "rating": "4.0", "desc": "South Indian"}
]

MENUS = {
    "1": [
        {"id": 101, "name": "Special Mutton Biryani", "price": 350, "desc": "Tender mutton chunks."},
        {"id": 102, "name": "Paneer Butter Masala", "price": 280, "desc": "Creamy tomato gravy."}
    ],
}

# --- 2. ROUTES ---

@app.route('/sw.js')
def serve_sw():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'sw.js')

@app.route('/')
def index():
    return render_template('index.html', stores=STORES)

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    return render_template('checkout.html')

@app.route('/place_order', methods=['POST'])
def place_order():
    order_data = request.json
    order_id = str(uuid.uuid4())[:8]
    order_data['order_id'] = order_id
    
    # On Netlify, we use /tmp/ for temporary file writing
    file_path = '/tmp/orders.json'
    try:
        orders = []
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                try:
                    orders = json.load(f)
                except:
                    orders = []
        
        orders.append(order_data)
        with open(file_path, 'w') as f:
            json.dump(orders, f)
            
    except Exception as e:
        print(f"Error: {e}")
        
    return jsonify({"status": "success", "order_id": order_id})

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/tracking')
def tracking():
    return render_template('tracking.html')

# --- 3. DEPLOYMENT HANDLERS ---

# This is for Netlify (Serverless)
def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)

# This is for Local Testing on your computer
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)