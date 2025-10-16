from uuid import uuid4

def generate_uuid():
    return str(uuid4())


# allowed file extensions for upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def is_allowed_file(filename):
    return ('.' in filename and 
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS)