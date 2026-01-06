from flask import Flask
import os

app = Flask(__name__)

def get_env_name():
    # Cloud Run automatically sets K_SERVICE to the name of your service
    service_name = os.getenv("K_SERVICE", "local-dev")
    
    if "prod" in service_name:
        return "production"
    elif "staging" in service_name:
        return "staging"
    elif "dev" in service_name:
        return "development"
    else:
        return "unknown"

@app.route("/")
def home():
    return {
        "message": "Cloud Build POC successful",
        "env": get_env_name(),
        "service_running": os.getenv("K_SERVICE", "Not on Cloud Run")
    }

if __name__ == "__main__":
    # Use PORT from env or default to 8080
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
