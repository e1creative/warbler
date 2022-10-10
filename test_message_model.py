"""Message model tests."""

# beginning code copied from test_user_model.py

# Does message properly register its writer?
# Does message fail if a user_id doesn't exist in the user's table?
# Does message fail if the text is longer than 140 characters?
# Does the User relationship work properly on the Messages model?

import os
from unittest import TestCase

from models import db, User, Message, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()



class MessageModelTestCase(TestCase):
    """Test Message model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def tearDown(self):
        """Rollback on exit"""

        db.session.rollback()


    def test_message_model(self):
        """Does basic model work?"""

        # create a user
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # create a message from the recently created user
        m = Message(
            user_id=u.id,
            text="Hello, testing message model!"
        )

        db.session.add(m)
        db.session.commit()

        # User should have 1 message
        self.assertEqual(len(u.messages), 1)

        # create another message from the recently created user
        m2 = Message(
            user_id=u.id,
            text="Hello, testing message model 2!"
        )

        db.session.add(m2)
        db.session.commit()

        # User should have 2 messages
        self.assertEqual(len(u.messages), 2)


    def test_message_model(self):
        """Does message properly register its writer?"""

        # create a user
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # create a message from the recently created user
        m = Message(
            user_id=u.id,
            text="Hello, testing message model!"
        )

        db.session.add(m)
        db.session.commit()

        # Message.user_id should return the id of the recently created user
        self.assertEqual(m.user_id, u.id)


    def test_fail_on_nonexistent_user_id(self):
        """Does message fail if a user_id doesn't exist in the user's table?"""

        # create a user
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # create a message from the recently created user with a user ID that doesn't exist
        m = Message(
            user_id=u.id+1,
            text="Hello, testing message model!"
        )

        db.session.add(m)

        from sqlalchemy.exc import IntegrityError
        self.assertRaises(IntegrityError, db.session.commit)


    def test_fail_on_overlength_message(self):
        """Does message fail if the text is longer than 140 characters?"""

        # create a user
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # create a message from the recently created user with a user ID that doesn't exist
        m = Message(
            user_id=u.id,
            text="Hello, testing message model!  Hello, testing message model!  Hello, testing message model!  Hello, testing message model!   Hello, testing message model!   Hello, testing message model!   Hello, testing message model!   Hello, testing message model!  Hello, testing message model!"
        )

        db.session.add(m)

        from sqlalchemy.exc import DataError
        self.assertRaises(DataError, db.session.commit)


    def test_message_user_relationship(self):
        """Does the User relationship work properly on the Messages model?"""

        # create a user
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # create a message from the recently created user with a user ID that doesn't exist
        m = Message(
            user_id=u.id,
            text="Hello, testing message model!"
        )

        db.session.add(m)
        db.session.commit()

        self.assertEqual(m.user_id, u.id)
