class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:1234@localhost:5432/BlogBackend'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'E:\\flask\\blog_backend\\images'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
