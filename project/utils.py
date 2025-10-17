from uuid import uuid4
from flask import session

def generate_uuid():
    return str(uuid4())


# allowed file extensions for upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def is_allowed_file(filename):
    return ('.' in filename and 
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS)

# check if user is logged in
def check_user_logged_in():
    if 'user' not in session or session['user']['userID'] == 0 or not session['logged_in']:
        return False
    return True

    
