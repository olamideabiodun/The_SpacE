from app import app
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        app.run()
    except Exception as e:
        logger.error(f"Failed to run app: {e}") 