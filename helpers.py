"""Contains helper functions that are useful elsewhere"""

import os

from flask import session
from models import User

CURR_USER_KEY = "curr_user"

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Log out user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
