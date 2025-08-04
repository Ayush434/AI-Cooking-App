# run.py
from app import create_app

app = create_app()

if __name__ == "__main__":
    # Allow external connections (for mobile testing)
    app.run(host='0.0.0.0', port=5000, debug=True)
