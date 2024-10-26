from flask import Blueprint, request, jsonify,current_app
from ..database.db_connect import connection

client = connection()
users= client.collection("users")  # Database

# Create a blueprint for user routes
user_bp = Blueprint('user', __name__)


# Get users ++
@user_bp.route('/users', methods=['GET'])
def get_all_users():
    # Fetch all users from Firestore
    all_users_query = users.stream()

    # Convert Firestore query results to a list of dictionaries (excluding password fields)
    all_users = [
        {**user.to_dict(), 'id': user.id} for user in all_users_query
        if 'password' in user.to_dict()  # Exclude password fields
    ]

    # Check if users list is empty
    if not all_users:
        return jsonify({'message': 'No users found'}), 400

    return jsonify(all_users), 200


# Get a single user by email ++ 

@user_bp.route('/users/<email>', methods=['GET'])
def get_one_user(email):
    if not email:
        return jsonify({'message': 'Email is required'}), 400
    
    # Query Firestore for the user by email
    user_query = users.where('email', '==', email).limit(1).stream()
    
    # Get the first result
    user = next(user_query, None)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404  # Changed status code for not found
    
    # Convert the Firestore document to a dictionary
    user_data = user.to_dict()
    # Exclude sensitive fields
    if 'password' in user_data:
        del user_data['password']
    
    return jsonify(user_data), 200

# Create a user ++
@user_bp.route('/users', methods=['POST'])
def create_user():
    bcrypt = current_app.config['bcrypt']  # Access bcrypt instance here

    # Get user data from the request
    data = request.json
    name = data.get('name')
    email = data.get('email')
    mobileno = data.get('mobileno')
    password = data.get('password')
    role = data.get('role')  # Get role from request, e.g., 'policyMaker' or 'user'
    policy = []

    # Validate role
    if role not in ['policyMaker', 'user']:
        return jsonify({'message': 'Invalid role'}), 400  # You can customize the roles as needed

    # Check for duplicate user (Firestore query)
    user_query = users.where('email', '==', email).stream()
    duplicate_user = next(user_query, None)  # Get the first result or None

    if duplicate_user:
        return jsonify({'message': 'User already exists'}), 409

    # Hash the password using bcrypt
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Insert new user into Firestore
    user_object = {
        'name': name,
        'email': email,
        'mobileno': mobileno,
        'password': hashed_password,
        'policy': policy,
        'role': role,  # Include role in the user object
    }

    users.add(user_object)  # Firestore add method for inserting a new document
    return jsonify({'message': f'User {email} created successfully'}), 201


# Get user by id ++
@user_bp.route('/getUser/<string:id>', methods=['GET'])
def get_user_id(id):
    if not id:
        return jsonify({'message': 'User ID Required'}), 400

    # Access the user document by ID
    user_ref = users.document(id)
    user = user_ref.get()

    if not user.exists:
        return jsonify({'message': 'User not found'}), 404  # 404 for not found

    # Convert Firestore document to dictionary
    user_data = user.to_dict()

    # Optional: Remove sensitive fields
    user_data.pop('password', None)

    return jsonify(user_data), 200



@user_bp.route('/', methods=['GET'])
def index():
    return jsonify({'message': 'Welcome to the user API'}), 200