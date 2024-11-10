import unittest
from datetime import datetime, timedelta
from app import app, db
from app.models import User, Post
from config import configur


class TestConfig(configur):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'  # Use in-memory database for testing


class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertTrue(u.check_password('cat'))
        self.assertFalse(u.check_password('dog'))

    def test_avatar(self):
        u = User(username='john', email='john@example.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                       'd4c74594d841139328695756648b6bd6'
                                       '?d=identicon&s=128'))

    def test_follow(self):
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        
        # Test that users aren't following anyone
        self.assertEqual(u1.following_count(), 0)
        self.assertEqual(u1.followers_count(), 0)

        # Test follow functionality
        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.following_count(), 1)
        self.assertEqual(u2.followers_count(), 1)

        # Test unfollow functionality
        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.following_count(), 0)
        self.assertEqual(u2.followers_count(), 0)

    def test_follow_posts(self):
        # Create four users
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        u3 = User(username='mary', email='mary@example.com')
        u4 = User(username='david', email='david@example.com')
        db.session.add_all([u1, u2, u3, u4])

        # Create four posts
        now = datetime.utcnow()
        p1 = Post(body="post from john", author=u1,
                 timestamp=now + timedelta(seconds=1))
        p2 = Post(body="post from susan", author=u2,
                 timestamp=now + timedelta(seconds=4))
        p3 = Post(body="post from mary", author=u3,
                 timestamp=now + timedelta(seconds=3))
        p4 = Post(body="post from david", author=u4,
                 timestamp=now + timedelta(seconds=2))
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        # Set up the followers
        u1.follow(u2)  # john follows susan
        u1.follow(u4)  # john follows david
        u2.follow(u3)  # susan follows mary
        u3.follow(u4)  # mary follows david
        db.session.commit()

        # Check the followed posts of each user
        f1 = list(u1.following_posts())
        f2 = list(u2.following_posts())
        f3 = list(u3.following_posts())
        f4 = list(u4.following_posts())
        
        # Assert the followed posts are correct
        self.assertEqual(f1, [p2, p4])
        self.assertEqual(f2, [p3])
        self.assertEqual(f3, [p4])
        self.assertEqual(f4, [])

    def test_user_login(self):
        # Create a test user
        u = User(username='test_user', email='test@example.com')
        u.set_password('test_password')
        db.session.add(u)
        db.session.commit()

        # Test valid login
        self.assertTrue(u.check_password('test_password'))
        
        # Test invalid login
        self.assertFalse(u.check_password('wrong_password'))

        # Test user exists in database
        user = db.session.scalar(
            db.select(User).filter_by(username='test_user'))
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test@example.com')


if __name__ == '__main__':
    unittest.main(verbosity=2) 