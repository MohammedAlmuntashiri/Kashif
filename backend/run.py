import os
from dotenv import load_dotenv

# Load .env from project root (one level up from backend/)
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
