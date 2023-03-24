"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows, Like

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        u1 = User.query.get(self.u1_id)

        # User should have no messages & no followers
        self.assertEqual(len(u1.messages), 0)
        self.assertEqual(len(u1.followers), 0)

    def test_authenticate(self):

        u1 = User.query.get(self.u1_id)

        self.assertEqual(User.authenticate("u1", "password"), u1)
        self.assertEqual(User.authenticate("u1", "wrong"), False)

    def test_is_followed_by(self):

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)
        
        u1.followers.append(u2)

        db.session.commit()

        self.assertEqual(u2.is_followed_by(u1), False)
        self.assertEqual(u1.is_followed_by(u2), True)

    def test_is_following(self):

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)
        
        u1.followers.append(u2)

        db.session.commit()

        self.assertEqual(u2.is_following(u1), True)
        self.assertEqual(u1.is_following(u2), False)

    def test_if_message_liked_by_user(self):

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        msg = Message(text="test_message")
        u1.messages.append(msg)
        u2.liked_messages.append(msg)

        db.session.commit()

        self.assertEqual(len(u2.likes), 1)