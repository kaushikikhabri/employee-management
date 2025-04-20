from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import text

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend to communicate

# Replace these credentials with yours
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:swing@localhost:5432/employee-db'
db = SQLAlchemy(app)

# Define your model
class User(db.Model):
    __tablename__ = 'login'  # Match your table name
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.Text)

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('username')
    password = data.get('password')
    
    #SECURE
    # user = User.query.filter_by(email=email, password=password).first()
    # if user:
    #     return jsonify({'success': True, 'message': 'Login successful!'}), 200
    # else:
    #     return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
    
    # 🚨 INSECURE version using raw SQL
    query = text(f"SELECT * FROM login WHERE email = '{email}' AND password = '{password}'")
    result = db.session.execute(query).fetchone()

    if result:
        return jsonify({'success': True, 'message': 'Login successful!'}), 200
    else:
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

if __name__ == '__main__':
    app.run(debug=True)
