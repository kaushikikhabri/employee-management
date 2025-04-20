from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import text
from datetime import datetime
import re



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



# Employee Model
class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(20), nullable=False)  # Add this line
    department = db.Column(db.String(100))
    salary = db.Column(db.Numeric(10, 2), nullable=False)  # Ensure this is defined correctly
    role = db.Column(db.String(100))
    join_date = db.Column(db.Date, nullable=False)


# Add a new employee
@app.route('/employees', methods=['POST'])
def add_employee():
    data = request.get_json()
    print("Received Data: ", data)

    required_fields = ['name', 'email', 'phone', 'department', 'role', 'salary', 'join_date']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'message': f'Missing required field: {field}'}), 400

    # Ensure the join_date is a proper datetime object
    try:
        join_date = datetime.strptime(data['join_date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'message': 'Invalid date format for join_date'}), 400

    # Check if email already exists
    if Employee.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400

    try:
        new_employee = Employee(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            department=data['department'],
            role=data['role'],
            salary=data['salary'],
            join_date=join_date  # Set the correctly formatted date
        )

        db.session.add(new_employee)
        db.session.commit()

        return jsonify({'message': 'Employee added successfully'}), 201

    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        print(f"Error occurred: {str(e)}")
        return jsonify({'message': f"Error: {str(e)}"}), 500
    
# Get employees with optional search
@app.route('/employees', methods=['GET'])
def get_employees():
    search = request.args.get('search', '')
    employees = Employee.query.filter(
        (Employee.name.ilike(f'%{search}%')) | 
        (Employee.email.ilike(f'%{search}%'))
    ).all()

    return jsonify([
        {
            'id': emp.id,
            'name': emp.name,
            'email': emp.email,
            'department': emp.department,
            'role': emp.role
        } for emp in employees
    ])

@app.route('/employees/<int:id>', methods=['GET'])
def get_employee(id):
    employee = Employee.query.get_or_404(id)  # Fetch employee by ID, or return 404 if not found
    return jsonify({
        'id': employee.id,
        'name': employee.name,
        'email': employee.email,
        'phone': employee.phone,
        'department': employee.department,
        'role': employee.role,
        'salary': str(employee.salary),  # Convert Decimal to string to avoid issues in JSON response
        'joinDate': employee.join_date.strftime('%Y-%m-%d')  # Format the date as string
    })


# Delete an employee
@app.route('/employees/<int:id>', methods=['DELETE'])
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    db.session.delete(employee)
    db.session.commit()
    return jsonify({'message': 'Employee deleted'}), 200

# # Update an employee
# @app.route('/employees/<int:id>', methods=['PUT'])
# def update_employee(id):
#     data = request.json
#     employee = Employee.query.get_or_404(id)

#     employee.name = data.get('name', employee.name)
#     employee.email = data.get('email', employee.email)
#     employee.department = data.get('department', employee.department)
#     employee.role = data.get('role', employee.role)

#     db.session.commit()
#     return jsonify({'message': 'Employee updated successfully'}), 200

@app.route('/employees/<int:id>', methods=['PUT'])
def update_employee(id):
    data = request.json  # Get the updated data sent in the request body
    employee = Employee.query.get_or_404(id)  # Fetch employee by ID, or return 404 if not found

    # Validate the phone number and email from the request data
    phone = data.get('phone')
    email = data.get('email')

    # Phone number validation (must be exactly 10 digits)
    if not phone or len(phone) != 10 or not phone.isdigit():
        return jsonify({'message': 'Phone number must be exactly 10 digits.'}), 400
    
    # Email validation (basic regex check)
    email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    if not email or not re.match(email_regex, email):
        return jsonify({'message': 'Please enter a valid email address.'}), 400

    # Update the employee details from the request data
    employee.name = data.get('name', employee.name)
    employee.email = email
    employee.phone = phone
    employee.department = data.get('department', employee.department)
    employee.role = data.get('role', employee.role)
    employee.salary = data.get('salary', employee.salary)
    employee.join_date = datetime.strptime(data.get('joinDate', employee.join_date.strftime('%Y-%m-%d')), '%Y-%m-%d')

    # Commit the changes to the database
    db.session.commit()

    # Return a success response
    return jsonify({'message': 'Employee updated successfully'}), 200


if __name__ == '__main__':
    app.run(debug=True)
