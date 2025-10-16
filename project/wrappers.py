from flask import session, redirect, flash, url_for
from functools import wraps

def only_admins(func):
    """Decorator to check if the user is an admin."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user' not in session or session['user']['userID'] == 0:
            flash('Please log in before moving on.', 'error')
            return redirect(url_for('main.login'))
        if not session['user']['role'] == 'Admin':
            flash('You do not have permission to view this page.', 'error')
            return redirect(url_for('main.index'))
        return func(*args, **kwargs)
    return wrapper

def only_vendors(func):
    """Decorator to check if the user is a vendor."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user' not in session or session['user']['user_id'] == 0:
            flash('Please log in before moving on.', 'error')
            return redirect(url_for('main.login'))
        if not session['user']['is_vendor']:
            flash('You do not have permission to view this page.', 'error')
            return redirect(url_for('main.index'))
        return func(*args, **kwargs)
    return wrapper