import csv
import datetime
import pytz
import requests
import urllib
import uuid

from flask import redirect, render_template, session
from functools import wraps

def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") == None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def admin_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") != 1:
            return apology("Not authorised", 401)
        return f(*args, **kwargs)

    return decorated_function

def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code

def generate_image(word):
    if not word:
        return None
    api_key = 'QOdTx9opI4ENrj8bVyqa3pcNJvtOCCnV5XP05e4GNigapY9AiCpfTUCd'
    url = f"https://api.pexels.com/v1/search?query={word}&per_page=1"
    headers = {'Authorization': api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if 'photos' in data and data['photos']:
            return data['photos'][0]['src']['large']
    return None
