import unittest
import tempfile
import os
from app.main import app
from app.db import get_db_connection, init_db

class URLShortenerTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.client = app.test_client()

        # Initialize DB and override the file-based DB
        with app.app_context():
            init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    def test_homepage_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Shorten Your URL', response.data)

    def test_anonymous_url_shortening(self):
        response = self.client.post('/', data={
            'original_url': 'http://example.com'
        }, follow_redirects=True)

        self.assertIn(b'Short URL:', response.data)

    def test_user_signup_and_login(self):
        # Sign up
        self.client.post('/signup', data={
            'username': 'testuser',
            'password': 'password'
        })

        # Login
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password'
        }, follow_redirects=True)

        self.assertIn(b'Logged in successfully', response.data)

    def test_custom_url_logged_in(self):
        # Sign up + Login
        self.client.post('/signup', data={
            'username': 'testuser2',
            'password': 'testpass'
        })
        self.client.post('/login', data={
            'username': 'testuser2',
            'password': 'testpass'
        })

        # Shorten URL with custom code
        response = self.client.post('/', data={
            'original_url': 'http://custom.com',
            'custom_code': 'custom123'
        }, follow_redirects=True)

        self.assertIn(b'Short URL: http://', response.data)

        # Visit short URL
        redirect_response = self.client.get('/custom123', follow_redirects=False)
        self.assertEqual(redirect_response.status_code, 302)
        self.assertIn('http://custom.com', redirect_response.location)

if __name__ == '__main__':
    unittest.main()
