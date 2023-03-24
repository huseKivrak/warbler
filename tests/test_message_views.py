"""Message View tests."""

# run these tests like:
#
#    FLASK_DEBUG=False python -m unittest test_message_views.py


from app import app, CURR_USER_KEY
import os
from unittest import TestCase

from models import db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app


app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# This is a bit of hack, but don't use Flask DebugToolbar

app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False

too_long = """
    Venmo gentrify thundercats narwhal, vinyl poutine yes plz enamel pin listicle keffiyeh.
    Fixie la croix crucifix, tilde coloring book enamel pin food truck hella biodiesel readymade swag.
    Vinyl hexagon flannel biodiesel street art 3 wolf moon 8-bit poutine lyft, green juice fanny pack.
    Bodega boys humblebrag schlitz flexitarian aesthetic tilde.
    """


class MessageBaseViewTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)
        db.session.flush()

        m1 = Message(text="m1-text", user_id=u1.id)
        m2 = Message(text="m2-text", user_id=u2.id)
        db.session.add_all([m1, m2])
        db.session.commit()

        self.u1_id = u1.id
        self.u2_id = u2.id
        self.m2_id = m2.id
        self.m2_id = m2.id

        self.client = app.test_client()


class MessageAddViewTestCase(MessageBaseViewTestCase):
    def test_add_message(self):
        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            # Now, that session setting is saved, so we can have
            # the rest of ours test
            resp = c.post("/messages/new", data={"text": "Hello"})

            self.assertEqual(resp.status_code, 302)

            added_msg = Message.query.filter_by(text="Hello").one()

            self.assertEqual(added_msg.user_id, self.u1_id)

    def test_bad_add_message(self):
        # Checks that msgs over max length are rejected
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post("/messages/new", data={
                "text": too_long}, follow_redirects=True)

            html = resp.get_data(as_text=True)
            self.assertIn("Messages can only be 140 characters or less!", html)

    def test_bad_user_add_message(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = None

            resp = c.post("/messages/new", data={
                "text": "no user"}, follow_redirects=True)

            html = resp.get_data(as_text=True)
            self.assertIn("Access unauthorized.", html)



class MessageDeleteViewTestCase(MessageBaseViewTestCase):
    def test_delete_message(self):
        with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.u1_id

                resp = c.post(f"/messages/{self.m1_id}/delete")
                self.assertEqual(resp.status_code, 302)

                msg = Message.query.one_or_none(self.u1_id)
                self.assertEqual(msg, None)

    def test_bad_user_delete_message(self):
        with self.client as c:
            with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.u2_id

            resp = c.post(f"/messages/{self.m1_id}/delete", follow_redirects=True)

            html = resp.get_data(as_text=True)
            self.assertIn("Access unauthorized.", html)

            msg = Message.query.one_or_none(self.u1_id)
            self.assertEqual(msg, None)

