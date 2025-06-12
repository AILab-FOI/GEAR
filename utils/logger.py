import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(levelname)s:%(name)s: %(message)s", filemode="w", filename="logs.log"
)

logger = logging.getLogger(__name__)
