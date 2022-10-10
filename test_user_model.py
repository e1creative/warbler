"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


# Example tests:
# Does the repr method work as expected?
# Does is_following successfully detect when user1 is following user2?
# Does is_following successfully detect when user1 is not following user2?
# Does is_followed_by successfully detect when user1 is followed by user2?
# Does is_followed_by successfully detect when user1 is not followed by user2?
# Does User.create successfully create a new user given valid credentials?
# Does User.create fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail?
# Does User.authenticate successfully return a user when given a valid username and password?
# Does User.authenticate fail to return a user when the username is invalid?
# Does User.authenticate fail to return a user when the password is invalid?


import os
from unittest import TestCase

from psycopg2 import IntegrityError

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


class UserModelTestCase(TestCase):
    """Test User model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    
        # User __repr__ should return "<User #{self.id}: {self.username}, {self.email}>
        self.assertEqual(str(u), f"<User #{u.id}: {u.username}, {u.email}>")      

    def test_user_is_following(self):
        """Does is_following successfully detect when user1 is following user2?"""
        u1 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )
        u2 = User(
            email="test3@test.com",
            username="testuser3",
            password="HASHED_PASSWORD"
        )
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        f = Follows(
            user_being_followed_id=u2.id,
            user_following_id=u1.id
        )
        db.session.add(f)
        db.session.commit()

        self.assertEqual(u1.is_following(u2), True)

    def test_user_is_not_following(self):
        """Does is_following successfully detect when user1 is not following user2?"""
        u1 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )
        u2 = User(
            email="test3@test.com",
            username="testuser3",
            password="HASHED_PASSWORD"
        )
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        self.assertEqual(u1.is_following(u2), False)


    def test_user_is_followed_by(self):
        """Does is_following successfully detect when user1 is following user2?"""
        u1 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )
        u2 = User(
            email="test3@test.com",
            username="testuser3",
            password="HASHED_PASSWORD"
        )
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        f = Follows(
            user_being_followed_id=u1.id,
            user_following_id=u2.id
        )
        db.session.add(f)
        db.session.commit()

        self.assertEqual(u1.is_followed_by(u2), True)


    def test_user_is_not_followed_by(self):
        """Does is_followed_by successfully detect when user1 is not followed by user2?"""
        u1 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )
        u2 = User(
            email="test3@test.com",
            username="testuser3",
            password="HASHED_PASSWORD"
        )
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        self.assertEqual(u1.is_followed_by(u2), False)


    def test_user_signup(self):
        """Does User.signup successfully create a new user given valid credentials?"""

        User.signup(username="TestUser", email="test@test.com", password="HASHED_PASSWORD", image_url="/static/images/warbler-hero.jpg")
        db.session.commit()

        user = User.query.all()

        self.assertEqual(user, user)


    def test_user_signup_fail_username(self):
        """Does User.signup fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail?"""

        User.signup(username="TestUser", email="test@test.com", password="HASHED_PASSWORD", image_url="/static/images/warbler-hero.jpg")
        db.session.commit()
        
        u1 = User(
            email="test1@test.com",
            username="TestUser",
            password="HASHED_PASSWORD"
        )

        # this should fail because u1.username is the same as u
        db.session.add(u1)

        from sqlalchemy.exc import IntegrityError
        self.assertRaises(IntegrityError, db.session.commit)


    def test_user_authenticate(self):
        """Does User.authenticate successfully return a user when given a valid username and password?"""

        # add a user to our db to test against, use User.signup to 
        u = User.signup(username="TestUser", email="test@test.com", password="HASHED_PASSWORD", image_url="/static/images/warbler-hero.jpg")
        db.session.commit()

        # check User.authenticate
        self.assertEqual(User.authenticate(username="TestUser", password="HASHED_PASSWORD"), u)


    def test_user_authenticate_fail_username(self):
        """Does User.authenticate fail to return a user when the username is invalid?"""

        # add a user to our db to test against, use User.signup to 
        User.signup(username="TestUser", email="test@test.com", password="HASHED_PASSWORD", image_url="/static/images/warbler-hero.jpg")
        db.session.commit()

        self.assertEqual(User.authenticate(username="TestUser2", password="HASHED_PASSWORD"), False)


    def test_user_authenticate_fail_password(self):
        """Does User.authenticate fail to return a user when the password is invalid?"""

        # add a user to our db to test against, use User.signup to 
        User.signup(username="TestUser", email="test@test.com", password="HASHED_PASSWORD", image_url="/static/images/warbler-hero.jpg")
        db.session.commit()

        self.assertEqual(User.authenticate(username="TestUser", password="HSHD_PWD"), False)
