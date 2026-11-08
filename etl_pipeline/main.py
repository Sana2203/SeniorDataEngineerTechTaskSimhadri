
import sqlite3
import requests
import json
from pathlib import Path

# API endpoints
POSTS_URL = "https://jsonplaceholder.typicode.com/posts"
USERS_URL = "https://jsonplaceholder.typicode.com/users"

# Your initials prefix
INITIALS = "sps"

# Database location: main project directory
DB_PATH = Path(__file__).resolve().parent.parent / f"{INITIALS}_blog.db"



# 1. EXTRACT


def extract_data():
    print("Extracting data from API...")

    posts_response = requests.get(POSTS_URL, timeout=30)
    users_response = requests.get(USERS_URL, timeout=30)

    # Check for API errors
    posts_response.raise_for_status()
    users_response.raise_for_status()

    posts = posts_response.json()
    users = users_response.json()

    if not isinstance(posts, list) or not isinstance(users, list):
        raise ValueError("API response must contain lists of posts and users")

    print(f"Extracted {len(posts)} posts")
    print(f"Extracted {len(users)} users")

    return posts, users



# 2. TRANSFORM


def transform_data(posts, users):
    print("Transforming data...")

    # Create user dictionary using user ID
    user_dict = {
        user["id"]: user
        for user in users
    }

    enriched_posts = []

    for post in posts:

        body = post.get("body", "")

        # Calculate post status
        status = "lengthy" if len(body) > 150 else "concise"

        # Find corresponding user
        user = user_dict.get(post.get("userId"), {})

        # Enrich post with user information
        enriched_post = {
            "id": post["id"],
            "userId": post["userId"],
            "title": post.get("title", ""),
            "body": body,
            "status": status,
            "name": user.get("name"),
            "username": user.get("username"),
            "email": user.get("email")
        }

        enriched_posts.append(enriched_post)

    # Preserve nested user JSON structures as JSON strings
    transformed_users = []

    for user in users:
        transformed_user = {
            "id": user["id"],
            "name": user.get("name"),
            "username": user.get("username"),
            "email": user.get("email"),
            "phone": user.get("phone"),
            "website": user.get("website"),
            "address_json": json.dumps(user.get("address", {})),
            "company_json": json.dumps(user.get("company", {}))
        }

        transformed_users.append(transformed_user)

    print(f"Transformed {len(enriched_posts)} posts")
    print(f"Transformed {len(transformed_users)} users")

    return enriched_posts, transformed_users



# 3. LOAD

def load_data(enriched_posts, users):
    print(f"Loading data into SQLite: {DB_PATH}")

    # Connect to database
    conn = sqlite3.connect(DB_PATH)

    try:
        # Enable foreign key validation
        conn.execute("PRAGMA foreign_keys = ON")

        cursor = conn.cursor()

        # Create users table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {INITIALS}_users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                username TEXT,
                email TEXT,
                phone TEXT,
                website TEXT,
                address_json TEXT,
                company_json TEXT
            )
        """)

        # Create posts table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {INITIALS}_posts (
                id INTEGER PRIMARY KEY,
                userId INTEGER,
                title TEXT,
                body TEXT,
                status TEXT,
                name TEXT,
                username TEXT,
                email TEXT,
                FOREIGN KEY (userId)
                    REFERENCES {INITIALS}_users(id)
            )
        """)

        # Insert or update users
        for user in users:
            cursor.execute(f"""
                INSERT INTO {INITIALS}_users (
                    id, name, username, email,
                    phone, website, address_json, company_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    username = excluded.username,
                    email = excluded.email,
                    phone = excluded.phone,
                    website = excluded.website,
                    address_json = excluded.address_json,
                    company_json = excluded.company_json
            """, (
                user["id"],
                user["name"],
                user["username"],
                user["email"],
                user["phone"],
                user["website"],
                user["address_json"],
                user["company_json"]
            ))

        # Insert or update enriched posts
        for post in enriched_posts:
            cursor.execute(f"""
                INSERT INTO {INITIALS}_posts (
                    id, userId, title, body, status,
                    name, username, email
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    userId = excluded.userId,
                    title = excluded.title,
                    body = excluded.body,
                    status = excluded.status,
                    name = excluded.name,
                    username = excluded.username,
                    email = excluded.email
            """, (
                post["id"],
                post["userId"],
                post["title"],
                post["body"],
                post["status"],
                post["name"],
                post["username"],
                post["email"]
            ))

        # Create index for faster user-based queries
        cursor.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_{INITIALS}_posts_userId
            ON {INITIALS}_posts(userId)
        """)

        conn.commit()

        print("Data loaded successfully!")

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()



# MAIN ETL EXECUTION


def main():
    print("\n========== ETL JOB STARTED ==========\n")

    try:
        # Extract
        posts, users = extract_data()

        # Transform
        enriched_posts, transformed_users = transform_data(
            posts, users
        )

        # Load
        load_data(enriched_posts, transformed_users)

        print("\n========== ETL JOB FINISHED ==========")

    except (requests.RequestException, ValueError, sqlite3.Error) as error:
        print(f"\nETL JOB FAILED: {error}")
        raise


if __name__ == "__main__":
    main()
