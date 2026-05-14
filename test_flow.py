import unittest
from app import create_app, init_db
import os
import sqlite3

class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        # Use a temporary database for testing
        self.app.config['DATABASE'] = 'instance/test_database.db'
        self.client = self.app.test_client()

        # Initialize the test database
        os.makedirs('instance', exist_ok=True)
        conn = sqlite3.connect(self.app.config['DATABASE'])
        with open('database/schema.sql', 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()

    def tearDown(self):
        if os.path.exists(self.app.config['DATABASE']):
            os.remove(self.app.config['DATABASE'])

    def test_full_flow(self):
        # 1. 開啟首頁 (需登入，所以會導向登入頁)
        rv = self.client.get('/')
        self.assertEqual(rv.status_code, 302)
        self.assertIn('/login', rv.headers['Location'])

        # 2. 註冊
        rv = self.client.post('/register', data=dict(
            username='testuser',
            password='testpassword',
            confirm_password='testpassword'
        ), follow_redirects=True)
        self.assertIn(b'testuser', rv.data) # Now on login page? Or register success message?
        self.assertEqual(rv.status_code, 200)

        # 3. 登入
        rv = self.client.post('/login', data=dict(
            username='testuser',
            password='testpassword'
        ), follow_redirects=True)
        self.assertIn(b'testuser', rv.data) # Dashboard
        self.assertEqual(rv.status_code, 200)

        # 4. 新增一筆資料
        rv = self.client.post('/records', data=dict(
            category='交通',
            action_name='car',
            parameter_value='10'
        ), follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        # Verify carbon calculation and suggestion
        self.assertIn(b'2.50 kg', rv.data) # 0.25 * 10
        self.assertIn(b'\xe6\x99\xba\xe6\x85\xa7\xe5\xbb\xba\xe8\xad\xb0', rv.data) # "智慧建議" in UTF-8

        # 5. 刪除資料 (假設 ID 為 1)
        rv = self.client.post('/records/1/delete', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'\xe7\xb4\x80\xe9\x8c\x84\xe5\xb7\xb2\xe5\x88\xaa\xe9\x99\xa4', rv.data) # "紀錄已刪除"

if __name__ == '__main__':
    unittest.main()
