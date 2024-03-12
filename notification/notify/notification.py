import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def notification(body):
    try:
        data = json.loads(body.decode("utf-8"))
        logger.info("Your order has been placed: %s", data)
    except Exception as e:
        logger.error("Failed to process notification: %s", e)


# Example usage:
# notification(body)
