from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

BASE_URL = "http://20.244.56.144/evaluation-service"


def fetch_users():
    response = requests.get(f"{BASE_URL}/users")
    if response.status_code == 200:
        return response.json()
    return {"users": []}


def fetch_posts(user_id):
    response = requests.get(f"{BASE_URL}/users/{user_id}/posts")
    if response.status_code == 200:
        return response.json()
    return {"posts": []}


@app.route('/users', methods=['GET'])
def get_users():
    users = fetch_users()
    return jsonify(users)


@app.route('/users/<int:user_id>/posts', methods=['GET'])
def get_user_posts(user_id):
    posts = fetch_posts(user_id)
    return jsonify(posts)


@app.route('/users/top', methods=['GET'])
def get_top_users():
    users = fetch_users()
    user_post_counts = {}

    for user_id in users["users"].keys():
        posts = fetch_posts(user_id)
        user_post_counts[user_id] = len(posts["posts"])

    top_users = sorted(user_post_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    response = {
        "users": [{user[0]: users["users"].get(user[0], "Unknown")} for user in top_users]
    }
    return jsonify(response)


@app.route('/posts', methods=['GET'])
def get_posts():
    post_type = request.args.get('type', 'latest')
    users = fetch_users()
    all_posts = []

    for user_id in users["users"].keys():
        posts = fetch_posts(user_id)
        for post in posts["posts"]:
            post["userId"] = user_id
        all_posts.extend(posts["posts"])

    if post_type == "popular":
        max_comments = max(all_posts, key=lambda x: x.get("comment_count", 0), default={"comment_count": 0})["comment_count"]
        popular_posts = [post for post in all_posts if post.get("comment_count", 0) == max_comments]
        response = {"posts": popular_posts}

    elif post_type == "latest":
        latest_posts = sorted(all_posts, key=lambda x: x.get("created_at", ""), reverse=True)[:5]
        response = {"posts": latest_posts}

    else:
        return jsonify({"error": "Invalid type parameter"}), 400

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)

