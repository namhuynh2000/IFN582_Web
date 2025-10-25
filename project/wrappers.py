from flask import session, redirect, flash, url_for
from functools import wraps
from project.utils import check_user_logged_in
from project.models import Role


def only_admins(func):
    """Decorator to check if the user is an admin."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if check_user_logged_in() is False:
            flash('Please log in before moving on', 'error')
            return redirect(url_for('main.login'))
        if not session['user']['role'] == Role.ADMIN.value:
            flash('You do not have permission to view this page', 'error')
            return redirect(url_for('main.index'))
        return func(*args, **kwargs)
    return wrapper


def only_vendors(func):
    """Decorator to check if the user is a vendor."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if check_user_logged_in() is False:
            flash('Please log in before moving on', 'error')
            return redirect(url_for('main.login'))
        if not session['user']['role'] == Role.VENDOR.value:
            flash('You do not have permission to view this page', 'error')
            return redirect(url_for('main.index'))
        return func(*args, **kwargs)
    return wrapper

