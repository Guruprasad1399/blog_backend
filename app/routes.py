from flask import Blueprint, jsonify, request,current_app,send_from_directory
from .models import User, Post
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from . import db, photos
from werkzeug.utils import secure_filename
import os
from flask import current_app
import re

main = Blueprint('main', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@main.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password are required!'}), 400

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id)
        return jsonify({'access_token': access_token, 'user_id': user.id }), 200
    else:
        return jsonify({'message': 'Invalid credentials!'}), 401

@main.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    email = data['email']
    password = data['password']
    confirm_password = data['confirmPassword']

    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({'message': 'User already exists!'}), 400

    if password != confirm_password:
        return jsonify({'message': 'Passwords do not match!'}), 400

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully!'}), 201

@main.route('/posts', methods=['GET'])
@jwt_required()
def get_posts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)
    posts = pagination.items

    return jsonify({
        'posts': [post.to_dict() for post in posts],
        'current_page': pagination.page,
        'total_pages': pagination.pages,
        'total_items': pagination.total
    }), 200

@main.route('/posts/<int:post_id>', methods=['GET'])
@jwt_required()
def get_post(post_id):
    post = Post.query.get_or_404(post_id)
    return jsonify(post.to_dict()), 200

@main.route('/posts', methods=['POST'])
@jwt_required()
def create_post():
    data = request.form
    title = data.get('title')
    body = data.get('body')
    user_id = get_jwt_identity()

    # Handle image upload
    image_filename = None
    if 'image' in request.files:
        image = request.files['image']
        if image:
            raw_filename = image.filename
            sanitized_filename = raw_filename.replace(' ', '-')
            sanitized_filename = re.sub(r'[^a-zA-Z0-9.\-_]', '', sanitized_filename)           
            image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], sanitized_filename))
            image_filename = sanitized_filename
    
    new_post = Post(title=title, body=body, user_id=user_id, image_filename=image_filename)
    
    db.session.add(new_post)
    db.session.commit()
    
    return jsonify({"message": "Post created", "post_id": new_post.id}), 201

@main.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(os.path.join(current_app.config['UPLOAD_FOLDER']), filename)