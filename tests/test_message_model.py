
from models import Message, User
from unittest import TestCase
from app import db



class TestMessage(TestCase):

    def setUp(self):
        User.query.delete()
        Message.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        test_msg1 = Message(text="test message 1", user_id=self.u1_id)
        test_msg2 = Message(text="test message 2", user_id=self.u2_id)
        db.session.commit()

        self.u1_id = u1.id
        self.u2_id = u2.id

        self.m1_id = test_msg1
        self.m2_id = test_msg2


    def tearDown(self):
        db.session.rollback()


    def test_message_model(self):
        u1 = User.query.get(self.u1_id)

        test_msg1 = Message.query.get(self.m1_id)

        self.assertEqual(u1.messages[0].text, test_msg1.text)
        self.assertEqual(test_msg1.user_id, u1.id)

