from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Set your own secret key for session management
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

@app.route("/")
def hello_world():
    return "<p>Test page</p>"

@app.route('/search',methods=['POST'])
def search_products():
    try:
        # Retrieve the keyword from the request body
        keyword = request.json['keyword']

        # Perform the search operation and retrieve the HTML content
        url = f'https://www.amazon.in/s?k={keyword.replace(" ","+")}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        content = response.content

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')

        # Extract the relevant information from the parsed HTML
        products = []
        results = soup.find_all('div', {'data-component-type': 's-search-result'})
        for result in results:
            title_elem = result.find('span', {'class': 'a-size-medium'})
            price_elem = result.find('span', {'class': 'a-price-whole'})
            image_elem = result.find('img', {'class': 's-image'})
            product_elem = 'https://www.amazon.in' + result.find('a', class_='a-link-normal')['href']
            rating_elem = result.find('span', {'class': 'a-icon-alt'})
            
            if title_elem and price_elem and image_elem:
                product = {
                    'title': title_elem.text.strip(),
                    'price': price_elem.text.strip(),
                    'image_url': image_elem.get('src'),
                    'product_url':product_elem,
                    'rating':rating_elem.text.strip(),
                }
                products.append(product)

        # Return the results as a JSON response
        return jsonify(products)

    except Exception as e:
        # Log the error message
        print('Error:', str(e))

        # Return an error response
        return jsonify({'error': 'An error occurred during the search.'}), 500

# User registration (signup) route
@app.route('/signup', methods=['POST'])
def signup():
    from models import User
    data = request.get_json()
    username = data['username']
    password = data['password']

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 400

    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'})

# User login route
@app.route('/login', methods=['POST'])
def login():
    from models import User
    data = request.get_json()
    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username).first()

    if user and user.password == password:
        session['user_id'] = user.id
        return jsonify({'message': 'Login successful'})
    else:
        return jsonify({'message': 'Invalid credentials'}), 401
    
@app.route('/wishlist', methods=['POST'])
def wishlist():
    from models import User, WishlistedProduct
    if 'user_id' not in session:
        return jsonify({'message': 'User not logged in'}), 401

    data = request.get_json()
    product_name = data['product_name']

    user_id = session['user_id']
    user = User.query.get(user_id)

    new_wishlist_item = WishlistedProduct(user_id=user.id, product_name=product_name)
    db.session.add(new_wishlist_item)
    db.session.commit()

    return jsonify({'message': 'Product added to wishlist'})

# Logout route
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logout successful'})
    
if __name__ == "__main__":
    db.create_all()
    app.run()


