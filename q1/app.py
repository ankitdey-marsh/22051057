from flask import Flask, jsonify
import requests
from collections import deque

app = Flask(__name__)

WINDOW_SIZE = 10
API_URLS = {
    "p": "http://20.244.56.144/evaluation-service/primes",
    "f": "http://20.244.56.144/evaluation-service/fibonacci",
    "e": "http://20.244.56.144/evaluation-service/even",
    "r": "http://20.244.56.144/evaluation-service/rand"
}

def get_auth_token():
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiZXhwIjoxNzQzNjAzNDg2LCJpYXQiOjE3NDM2MDMxODYsImlzcyI6IkFmZm9yZG1lZCIsImp0aSI6IjA1MDRkMjNlLTkzZTctNGVhZC1iZjAzLTM1ZTU2NzllNGIyYyIsInN1YiI6IjIyMDUxMDU3QGtpaXQuYWMuaW4ifSwiZW1haWwiOiIyMjA1MTA1N0BraWl0LmFjLmluIiwibmFtZSI6ImFua2l0IGRleSIsInJvbGxObyI6IjIyMDUxMDU3IiwiYWNjZXNzQ29kZSI6Im53cHdyWiIsImNsaWVudElEIjoiMDUwNGQyM2UtOTNlNy00ZWFkLWJmMDMtMzVlNTY3OWU0YjJjIiwiY2xpZW50U2VjcmV0IjoiSllZUVhWdkFDeXRVQVREcSJ9.j6x3Wlzo4w6lAmj0hRK0y6xLSoFfdO4EGsCVcF1Y8Sk"

window = deque(maxlen=WINDOW_SIZE)

def fetch_numbers(number_id):
    url = API_URLS.get(number_id)
    if not url:
        return []

    headers = {
        "Authorization": f"Bearer {get_auth_token()}"
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        numbers = list(set(response.json().get("numbers", [])))
        print(f"Fetched numbers for {number_id}: {numbers}")
        return numbers
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error: {req_err}")

    return []

@app.route('/numbers/<number_id>', methods=['GET'])
def get_numbers(number_id):
    global window
    prev_state = list(window)
    new_numbers = fetch_numbers(number_id)
    
    if new_numbers:
        for num in new_numbers:
            if num not in window:
                window.append(num)

    avg = round(sum(window) / len(window), 2) if window else 0

    return jsonify({
        "windowPrevState": prev_state,
        "windowCurrState": list(window),
        "numbers": new_numbers,
        "avg": avg
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9876, debug=True)
