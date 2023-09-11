from flask import Blueprint, jsonify, request
from .models import User, Post
from flask_jwt_extended import create_access_token, jwt_required
from . import db

main = Blueprint('main', __name__)

@main.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password are required!'}), 400

    user = User.query.filter_by(email=email).first()

    # Use the check_password method to verify the password
    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id)  # Create the token
        return jsonify({'access_token': access_token,'user_id': user.id }), 200
    else:
        return jsonify({'message': 'Invalid credentials!'}), 401


@main.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    email = data['email']
    password = data['password']
    confirm_password = data['confirmPassword']

    # Check if user already exists
    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({'message': 'User already exists!'}), 400

    # Check password confirmation
    if password != confirm_password:
        return jsonify({'message': 'Passwords do not match!'}), 400

    # Create new user and add to the database
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
    data = request.json
    if not data.get('title') or not data.get('body') or not data.get('author_id'):
        return jsonify({'message': 'Title, body, and author_id are required!'}), 400
    post = Post(title=data['title'], body=data['body'], user_id=data['author_id'])
    db.session.add(post)
    db.session.commit()
    return jsonify({'message': 'Post Created Successfully!'}), 201

