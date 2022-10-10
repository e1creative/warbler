"""User view tests."""

# beginning code copied from test_message_views.py

import os
from unittest import TestCase

from flask import session

from models import db, connect_db, Message, User, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']


class UserViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        # create an initial user
        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()


    def test_signup(self):
        """Test the signup view"""
        with app.test_client() as client:
            resp = client.get('/signup')
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Sign me up!", html)


    def test_signup_post(self):
        """ Test the signup view POST route with data."""
        with app.test_client() as client:
            data = {
                'username': 'testuser2',
                'password': 'password',
                'email': 'test2@test.com'
            }
            resp = client.post('/signup', data=data)


            # check that our response code is the redirect coming from the view
            self.assertEqual(resp.status_code, 302)


            u = User.query.filter_by(username="testuser2").first()
            
            # check that the user that we added is added to the session
            self.assertEqual(session[CURR_USER_KEY], u.id)


    def test_login_get(self):
        """ Test the signup view GET route with data."""
        with app.test_client() as client:
            resp = client.get('/login')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Welcome back", html)


    def test_login_post(self):
        """ Test the login view POST route with data."""
        with app.test_client() as client:
            data = {
                    'username': 'testuser',
                    'password': 'testuser',
                }
            # following the redirect to the "/" route
            resp = client.post('/login', data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            # username is test user and it should be flashed on the page for a successful redirect
            self.assertIn("Hello, testuser", html)


    def test_logout(self):
        """ Test the signup view GET route with data."""
        with app.test_client() as client:
            # following the redirect to the "/" route
            resp = client.get('/logout', follow_redirects=True)
            html = resp.get_data(as_text=True)

            # check that we are redirected to the login page
            self.assertEqual(resp.status_code, 200)
            self.assertIn("You have been logged out successfully!", html)

            # check that session has been cleared after running do_logout()
            self.assertNotIn(CURR_USER_KEY, session)


    def test_list_users(self):
        """ Test list users GET route"""
        with app.test_client() as client:
            resp = client.get('/users')
            html = resp.get_data(as_text=True)

            # check that we are redirected to the login page
            self.assertEqual(resp.status_code, 200)
            # check that our user shows up in the list of users
            self.assertIn("@testuser", html)


    def test_users_show(self):
        """ Test user show profile ROUTE"""
        with app.test_client() as client:

            # query our newly created user (at the top) to get the id
            u = User.query.filter_by(username="testuser").first()

            # use the id to check his page
            resp = client.get(f'/users/{u.id}')
            html = resp.get_data(as_text=True)

            # check that we are redirected to the login page
            self.assertEqual(resp.status_code, 200)
            # check that our username is in the html
            self.assertIn("@testuser", html)
    

#############################################
    def test_show_following(self):
        """ Test list user show following GET route"""
        with app.test_client() as client:

            # query our newly created user (at the top) to get the id
            u = User.query.filter_by(username="testuser").first()

            resp = client.get(f'/users/{u.id}/following')

            # check that we are redirected to the home page, since we are currently NOT logged in
            self.assertEqual(resp.status_code, 302)

            # now set our session ID and re-visit the page to get a 200 response
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = client.get(f'/users/{u.id}/following')
            self.assertEqual(resp.status_code, 200)


    def test_show_followers(self):
        """ Test list user show followers GET route"""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = client.get(f'/users/{self.testuser.id}/followers')

            self.assertEqual(resp.status_code, 200)


    def test_show_likes(self):
        """ Test list user show followers GET route"""
        with app.test_client() as client:
            # query our newly created user (at the top) to get the id
            u = User.query.filter_by(username="testuser").first()

            resp = client.get(f'/users/{u.id}/likes')

            # check that we are redirected to the home page, since we are currently NOT logged in
            self.assertEqual(resp.status_code, 302)

            # now set our session ID and re-visit the page to get a 200 response
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = client.get(f'/users/{u.id}/likes')
            self.assertEqual(resp.status_code, 200)


    def test_add_follow(self):
        """ Test add following POST route"""
        with app.test_client() as client:
            # log in our testuser
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # create a new user
            u2 = User(username="testuser2", email="test2@test.com", password="password")

            db.session.add(u2)
            db.session.commit()

            # send to post request to follow
            resp = client.post(f'/users/follow/{u2.id}')

            # check that we are redirected to the followers list page
            self.assertEqual(resp.status_code, 302)


    def test_stop_following(self):
        """ Test stop following POST route"""
        with app.test_client() as client:
            # log in our testuser
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # create a new user
            u2 = User(username="testuser2", email="test2@test.com", password="password")

            db.session.add(u2)
            db.session.commit()

            # testuser follows newly created user
            f = Follows(user_being_followed_id=u2.id , user_following_id=sess[CURR_USER_KEY])

            db.session.add(f)
            db.session.commit()

            # send a post request to unfollow
            resp = client.post(f'/users/follow/{u2.id}')

            self.assertEqual(resp.status_code, 302)


    def test_add_remove_likes(self):
        """ Test likes POST route"""
        with app.test_client() as client:
            # log in our testuser
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # create a new user
            u2 = User(username="testuser2", email="test2@test.com", password="password")

            db.session.add(u2)
            db.session.commit()

            # create a message for our new user
            m = Message(text="Testing our message likes!", user_id=u2.id)

            db.session.add(m)
            db.session.commit()

            # print('')
            # print('*************')
            # print(m.id)
            # print('*************')
            # print('')

            # send the post request to add the like
            resp = client.post(f'/users/add_like{m.id}')

            # check that self.testuser.likes returns a list
            print('')
            print('*************')
            print(resp.status_code)
            print('*************')
            print('')

            # check that we are redirected to the login page
            # self.assertEqual(, [])


    def test_profile_get(self):
        """ Test show profile GET route"""
        with app.test_client() as client:

            # uses session to get the user ID.  if user is logged in we should get a 200
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = client.get('/users/profile')
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Edit Your Profile.", html)


    def test_profile_post(self):
        """ Test list user show followers GET route"""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = client.post('/users/profile')

            # check that we are redirected to the login page
            self.assertEqual(resp.status_code, 302)


    def test_delete_user(self):
        """ Test list user show followers GET route"""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            # user is defined using the session
            resp = client.post('/users/delete')

            # check that we are redirected to the login page
            self.assertEqual(resp.status_code, 302)




#     def test_logged_view_users_followers_following(self):
#             """When you’re logged in, can you see the follower / following pages for any user?
# When you’re logged out, are you disallowed from visiting a user’s follower / following pages?"""
#         with app.test_client() as client:
#             resp = client.post('/users/delete', data)

#             # check that we are redirected to the login page
#             self.assertEqual(resp.status_code, 200)


#     def test_add_message(self):
#         """When you’re logged in, can you add a message as yourself?"""

#                 with app.test_client() as client:
#             resp = client.post('/users/delete', data)

#             # check that we are redirected to the login page
#             self.assertEqual(resp.status_code, 200)


#     def test_delete_message(self):
#         """When you’re logged in, can you delete a message as yourself?"""

#                 with app.test_client() as client:
#             resp = client.post('/users/delete', data)

#             # check that we are redirected to the login page
#             self.assertEqual(resp.status_code, 200)


#     def test_logged_out_add_message(self):
#         """When you’re logged out, are you prohibited from adding messages?"""

#                 with app.test_client() as client:
#             resp = client.post('/users/delete', data)

#             # check that we are redirected to the login page
#             self.assertEqual(resp.status_code, 200)


#     def test_logged_out_delete_message(self):
#         """When you’re logged out, are you prohibited from deleting messages?"""

#                 with app.test_client() as client:
#             resp = client.post('/users/delete', data)

#             # check that we are redirected to the login page
#             self.assertEqual(resp.status_code, 200)


#     def test_add_message_as_dif_user (self)
#         """When you’re logged in, are you prohibiting from adding a message as another user?"""

#                 with app.test_client() as client:
#             resp = client.post('/users/delete', data)

#             # check that we are redirected to the login page
#             self.assertEqual(resp.status_code, 200)


#     def test_dif_message_as_dif_user (self)
#         """When you’re logged in, are you prohibiting from deleting a message as another user?"""

#                 with app.test_client() as client:
#             resp = client.post('/users/delete', data)

#             # check that we are redirected to the login page
#             self.assertEqual(resp.status_code, 200)
