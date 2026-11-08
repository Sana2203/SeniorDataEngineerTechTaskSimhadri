
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from etl_pipeline import main as etl


class TestETLPipeline(unittest.TestCase):

    def setUp(self):
        self.users = [
            {
                "id": 1,
                "name": "Test User",
                "username": "testuser",
                "email": "test@example.com",
                "phone": "1234567890",
                "website": "example.com",
                "address": {
                    "city": "Hyderabad",
                    "zipcode": "500001"
                },
                "company": {
                    "name": "Test Company"
                }
            }
        ]

        self.posts = [
            {
                "id": 1,
                "userId": 1,
                "title": "Short Post",
                "body": "This is a short post."
            },
            {
                "id": 2,
                "userId": 1,
                "title": "Long Post",
                "body": "A" * 200
            }
        ]

    def test_extract_data(self):
        posts_response = Mock()
        posts_response.json.return_value = self.posts

        users_response = Mock()
        users_response.json.return_value = self.users

        with patch(
            "etl_pipeline.main.requests.get",
            side_effect=[posts_response, users_response]
        ) as mock_get:

            posts, users = etl.extract_data()

        self.assertEqual(len(posts), 2)
        self.assertEqual(len(users), 1)
        self.assertEqual(mock_get.call_count, 2)

    def test_transform_data(self):
        enriched_posts, transformed_users = etl.transform_data(
            self.posts, self.users
        )

        self.assertEqual(len(enriched_posts), 2)
        self.assertEqual(len(transformed_users), 1)

        self.assertEqual(enriched_posts[0]["status"], "concise")
        self.assertEqual(enriched_posts[1]["status"], "lengthy")

        self.assertEqual(enriched_posts[0]["name"], "Test User")
        self.assertEqual(enriched_posts[0]["email"], "test@example.com")

    def test_user_json_transformation(self):
        _, transformed_users = etl.transform_data(
            self.posts, self.users
        )

        address = json.loads(transformed_users[0]["address_json"])
        company = json.loads(transformed_users[0]["company_json"])

        self.assertEqual(address["city"], "Hyderabad")
        self.assertEqual(company["name"], "Test Company")

    def test_load_data(self):
        enriched_posts, transformed_users = etl.transform_data(
            self.posts, self.users
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            test_db = Path(temp_dir) / "test_blog.db"

            with patch.object(etl, "DB_PATH", test_db):
                etl.load_data(enriched_posts, transformed_users)

            conn = sqlite3.connect(test_db)

            users = conn.execute(
                "SELECT * FROM sps_users"
            ).fetchall()

            posts = conn.execute(
                "SELECT * FROM sps_posts"
            ).fetchall()

            conn.close()

            self.assertEqual(len(users), 1)
            self.assertEqual(len(posts), 2)


if __name__ == "__main__":
    unittest.main()
