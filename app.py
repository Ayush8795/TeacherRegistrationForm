from flask import Flask, request, jsonify, render_template
from bson.objectid import ObjectId
from datetime import datetime
import os
from flask_cors import CORS
from pymongo.mongo_client import MongoClient


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

uri = os.getenv('CONNECTION_STRING')
client = MongoClient(uri)

# Configure MongoDB connection
teachers_collection = client['teacherRegister']['teachers']

@app.route('/')
def index():
    """Serve the registration form."""
    return render_template('index.html')

@app.route('/api/teachers', methods=['POST'])
def add_teacher():
    """Add a new teacher to the database."""
    try:
        # Get data from request
        teacher_data = request.json
        
        # Basic validation
        required_fields = ['name', 'email', 'phone', 'gender', 'dob', 'school']
        for field in required_fields:
            if field not in teacher_data or not teacher_data[field]:
                return jsonify({'error': f'Field {field} is required'}), 400
        
        # Check if email already exists
        if teachers_collection.find_one({'email': teacher_data['email']}):
            return jsonify({'error': 'Email already registered'}), 400
            
        # Format date (assuming it's in YYYY-MM-DD format)
        try:
            dob_date = datetime.strptime(teacher_data['dob'], '%Y-%m-%d')
            teacher_data['dob'] = dob_date
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
            
        # Add timestamp
        teacher_data['created_at'] = datetime.now()
        
        # Insert into MongoDB
        result = teachers_collection.insert_one(teacher_data)
        
        # Return success response
        return jsonify({
            'message': 'Teacher registration successful',
            'id': str(result.inserted_id)
        }), 201
        
    except Exception as e:
        # Log the error (in a production app)
        print(f"Error: {str(e)}")
        return jsonify({'error': 'An error occurred while processing your request'}), 500

@app.route('/api/teachers', methods=['GET'])
def get_teachers():
    """Get all teachers from the database."""
    try:
        teachers = list(teachers_collection.find())
        
        # Convert ObjectId to string for each teacher
        for teacher in teachers:
            teacher['_id'] = str(teacher['_id'])
            # Format date for display
            if 'dob' in teacher and isinstance(teacher['dob'], datetime):
                teacher['dob'] = teacher['dob'].strftime('%Y-%m-%d')
            if 'created_at' in teacher and isinstance(teacher['created_at'], datetime):
                teacher['created_at'] = teacher['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify(teachers), 200
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': 'An error occurred while retrieving data'}), 500

@app.route('/api/teachers/<id>', methods=['GET'])
def get_teacher(id):
    """Get a specific teacher by ID."""
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(id):
            return jsonify({'error': 'Invalid ID format'}), 400
            
        teacher = teachers_collection.find_one({'_id': ObjectId(id)})
        
        if not teacher:
            return jsonify({'error': 'Teacher not found'}), 404
            
        # Convert ObjectId to string
        teacher['_id'] = str(teacher['_id'])
        
        # Format date for display
        if 'dob' in teacher and isinstance(teacher['dob'], datetime):
            teacher['dob'] = teacher['dob'].strftime('%Y-%m-%d')
        if 'created_at' in teacher and isinstance(teacher['created_at'], datetime):
            teacher['created_at'] = teacher['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify(teacher), 200
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': 'An error occurred while retrieving data'}), 500

if __name__ == '__main__':
    # Create folder for templates if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Create index.html template file from the frontend code
    # In a real application, you would have separate frontend and backend repos
    # This is just for convenience in this example
    app.run(debug=True)