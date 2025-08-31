from functools import wraps
from flask import session,redirect,url_for
from app.model import User

def admin_required(f):
    def wrap(*args,**kwargs):
        if session.get('is_admin'):
            return f(*args,**kwargs)
        return redirect(url_for('register.login')) 
    return wrap

