import jwt
import bcrypt
from flask import Blueprint, request, jsonify, current_app, make_response
from ..database.db_connect import connection
import os
from functools import wraps
from datetime import datetime, timedelta
from dotenv import load_dotenv
import re
from pytesseract import pytesseract
from pdf2image import convert_from_path
from flask import request, jsonify, current_app
from google.cloud import storage
from PIL import Image
import firebase_admin
from firebase_admin import credentials, storage 
from werkzeug.utils import secure_filename
# Load environment variables from .env file
load_dotenv()

data = connection()
client = connection()
bucket = storage.bucket()
users = client.collection("users") 
policies = client.collection("policy") 


# Create a blueprint for user routes
policy_bp = Blueprint('policy', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('jwt')
        if not token:
            return jsonify({'message': 'Unauthorized: no cookie store'}), 401

        try:
            decoded_token = jwt.decode(token, os.getenv('AUTH_TOKEN'), algorithms=["HS256"])
            return f(decoded_token, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Forbidden: invalid token'}), 403

    return decorated

@policy_bp.route('/create', methods=['POST'])
@token_required
def create_policy(decoded_token):
    # Get the creator's ID from the decoded token
    print(decoded_token)

    creator_id = decoded_token['UserInfo']['id']

    data = request.json
    title = data.get('title')
    description = data.get('description')
    type = data.get('type')
    coverage = data.get("coverage")
    plan = data.get("plan")
    company = data.get("company")
    hyperlink = data.get("hyperlink")
    img = data.get("img")

    policy = {
        'title': title,
        'description': description,
        'type': type,
        'coverage': coverage,
        'plan': plan,
        'creator': creator_id,  # Use the creator ID from the token
        'company': company,
        'hyperlink': hyperlink,
        'img': img
    }

    # Add the policy to Firestore
    policy_ref = policies.add(policy)  # Use add() to create a new document in policies collection

    return jsonify({'message': 'Policy created successfully'}), 201



# Get all policies
@policy_bp.route('/policies', methods=['GET'])
def get_all_policies():
    policies_list = []
    # Query Firestore for all policies
    for policy in policies.stream():
        policy_data = policy.to_dict()
        policy_data['id'] = policy.id  # Include Firestore document ID
        policies_list.append(policy_data)

    return jsonify(policies_list), 200

# Get policies by type
@policy_bp.route('/policies/type/<string:type>', methods=['GET'])
def get_policies_by_type(type):
    policies_list = []
    # Query Firestore for policies by type
    query = policies.where('type', '==', type).stream()

    for policy in query:
        policy_data = policy.to_dict()
        policy_data['id'] = policy.id  # Include Firestore document ID
        policies_list.append(policy_data)

    if not policies_list:
        return jsonify({'message': 'No policies found for this type'}), 404

    return jsonify(policies_list), 200

# Get policy by ID
@policy_bp.route('/policy/<string:policy_id>', methods=['GET'])
def get_policy_by_id(policy_id):
    # Query Firestore for the policy by ID
    policy_ref = policies.document(policy_id)
    policy = policy_ref.get()

    if not policy.exists:
        return jsonify({'message': 'Policy not found'}), 404

    policy_data = policy.to_dict()
    policy_data['id'] = policy.id  # Include Firestore document ID

    return jsonify(policy_data), 200


ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
UPLOAD_FOLDER = 'uploads'

# Helper function to check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@policy_bp.route('/buy_policy', methods=['POST'])
@token_required
def buy_policy(decoded_token):
    email = decoded_token['UserInfo'].get('email')  # Get the user's email from the decoded token
    print(decoded_token)
    if not email:
        return jsonify({'message': 'Unauthorized: no user email found in token'}), 401

    data = request.json
    policy_id = data.get('policy_id')

    if not policy_id:
        return jsonify({'message': 'Policy ID is required'}), 400

    # Retrieve the policy to ensure it exists
    policy_ref = policies.document(policy_id)
    policy = policy_ref.get()

    if not policy.exists:
        return jsonify({'message': 'Policy not found'}), 404

    policy_data = policy.to_dict()
    creator_id = policy_data.get('creator')  # Assuming creator ID is stored in the policy document

    # Retrieve the user who is buying the policy
    user_query = users.where('email', '==', email).limit(1).stream()
    user = next(user_query, None)

    if not user:
        return jsonify({'message': 'User not found'}), 404

    user_data = user.to_dict()
    user_id = user.id  # ID of the user buying the policy

    # Update user's bought policies
    bought_policies = user_data.get('policy', [])
    bought_policies.append(policy_id)  # Add the new policy ID

    # Update Firestore user document
    users.document(user.id).update({'policy': bought_policies})

    policy_ref = policies.document(policy_id)
    policy_doc = policy_ref.get()

    if not policy_doc.exists:
        return jsonify({'message': 'Policy not found'}), 404

    # Retrieve existing policy data and add user ID to buyers list
    policy_data = policy_doc.to_dict()
    buyers = policy_data.get('buyers', [])
    
    if user_id in buyers:
        return jsonify({'message': 'Policy already purchased by this user'}), 409

    buyers.append(user_id)  # Add the user's ID to the buyers list
    policy_ref.update({'buyers': buyers})  # Update the policy's buyers list in Firestore

    return jsonify({'message': 'Policy purchased successfully', 'policy_id': policy_id}), 201


@policy_bp.route('/storage', methods=['POST'])
@token_required
def upload_kyc_image(decoded_token):
    try:        
        email = decoded_token['UserInfo'].get('email')
        if not email:
            return jsonify({'message': 'Unauthorized: no user email found in token'}), 401  # Get the user's email from the decoded token
        # Check if the image and userId are provided
        if 'image' not in request.files or 'userId' not in request.form:
            return jsonify({'error': 'Image and userId are required'}), 400
        user_query = users.where('email', '==', email).limit(1).stream()
        user = next(user_query, None)

        if not user:
            return jsonify({'message': 'User not found'}), 404

        user_data = user.to_dict()
        user_id = user.id 
        image = request.files['image']
        
        # Secure the filename and build the path within Firebase Storage
        filename = secure_filename(image.filename)
        firebase_path = f'KYC/{user_id}/{filename}'

        # Create a blob (file) in the Firebase Storage and upload image data
        blob = bucket.blob(firebase_path)
        blob.upload_from_file(image, content_type=image.content_type)

        # Make the image publicly accessible and get the URL
        blob.make_public()
        image_url = blob.public_url

        return jsonify({'message': 'Image uploaded successfully', 'image_url': image_url}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@policy_bp.route('/storage/multiple', methods=['POST'])
@token_required
def upload_multiple_files(decoded_token):
    try:
        email = decoded_token['UserInfo'].get('email')
        if not email:
            return jsonify({'message': 'Unauthorized: no user email found in token'}), 401

        # Check if required files are provided
        required_files = ['before_image', 'after_image', 'video', 'fir_image']
        if not all(file in request.files for file in required_files) or 'link' not in request.form:
            return jsonify({'error': 'All required files and link must be provided'}), 400
        
        user_query = users.where('email', '==', email).limit(1).stream()
        user = next(user_query, None)

        if not user:
            return jsonify({'message': 'User not found'}), 404

        user_data = user.to_dict()
        user_id = user.id

        # Store URLs of uploaded files
        uploaded_files_urls = {}

        # Process each file
        for file_key in required_files:
            if file_key in request.files:
                file = request.files[file_key]
                filename = secure_filename(file.filename)
                firebase_path = f'KYC/{user_id}/{file_key}/{filename}'  # Create a specific path for each file type

                # Create a blob (file) in the Firebase Storage and upload file data
                blob = bucket.blob(firebase_path)
                blob.upload_from_file(file, content_type=file.content_type)

                # Make the file publicly accessible and get the URL
                blob.make_public()
                uploaded_files_urls[file_key] = blob.public_url

        # Handle the link (as a string) separately
        link = request.form['link']
        uploaded_files_urls['link'] = link

        return jsonify({
            'message': 'Files and link uploaded successfully',
            'file_urls': uploaded_files_urls
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@policy_bp.route('/', methods=['GET'])
def index():
    return jsonify({'message': 'Welcome to the user API'}), 200