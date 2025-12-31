from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def home():
    return {
        "message": "Cloud Build POC successful",
        "env": os.getenv("ENV", "unknown")
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
