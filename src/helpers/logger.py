import logging
import os

from logstash_formatter import LogstashFormatterV1  # type: ignore
from config.env import LOGSTASH_URL, LOGSTASH_TOKEN, LOGSTASH_ENV

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("worker")

try:
	import socket
	host, port = LOGSTASH_URL.split(":")
	port = int(port)
	logstash_handler = logging.handlers.SocketHandler(host, port)
	logstash_handler.setFormatter(LogstashFormatterV1())

	logstash_handler.addFilter(lambda record: setattr(record, 'environment', LOGSTASH_ENV) or True)
	logstash_handler.addFilter(lambda record: setattr(record, 'token', LOGSTASH_TOKEN) or True)
	logstash_handler.addFilter(lambda record: setattr(record, 'app', 'calcula-ai-worker') or True)
	logstash_handler.addFilter(lambda record: setattr(record, 'kind', 'worker') or True)
	logstash_handler.addFilter(lambda record: setattr(record, 'type', 'json') or True)

	logger.addHandler(logstash_handler)
except Exception as e:
	logger.warning(f"Could not set up Logstash handler: {e}")