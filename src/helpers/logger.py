import logging
import os
import socket

from logstash_formatter import LogstashFormatterV1  # type: ignore
from config.env import LOGSTASH_URL, LOGSTASH_TOKEN, LOGSTASH_ENV

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("worker")

class TCPJSONSocketHandler(logging.Handler):
	def __init__(self, host: str, port: int, timeout: float = 3.0):
		super().__init__()
		self.host = host
		self.port = port
		self.timeout = timeout
		self.sock: socket.socket | None = None
		self._connect()

	def _connect(self) -> None:
		try:
			self.sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
			self.sock.settimeout(self.timeout)
		except Exception:
			self.sock = None

	def emit(self, record: logging.LogRecord) -> None:
		try:
			msg = self.format(record)
			data = (msg + "\n").encode("utf-8")
			if not self.sock:
				self._connect()
			if self.sock:
				self.sock.sendall(data)
		except Exception:
			self.handleError(record)

	def close(self) -> None:
		try:
			if self.sock:
				try:
					self.sock.close()
				except Exception:
					pass
				self.sock = None
		finally:
			super().close()

try:
	host, port = LOGSTASH_URL.split(":")
	port = int(port)
	if not any(isinstance(h, TCPJSONSocketHandler) for h in logger.handlers):
		logstash_handler = TCPJSONSocketHandler(host, port)
		logstash_handler.setFormatter(LogstashFormatterV1())

		logstash_handler.addFilter(lambda record: setattr(record, 'environment', LOGSTASH_ENV) or True)
		logstash_handler.addFilter(lambda record: setattr(record, 'token', LOGSTASH_TOKEN) or True)
		logstash_handler.addFilter(lambda record: setattr(record, 'app', 'calcula-ai-worker') or True)
		logstash_handler.addFilter(lambda record: setattr(record, 'kind', 'worker') or True)
		logstash_handler.addFilter(lambda record: setattr(record, 'type', 'json') or True)

		logger.addHandler(logstash_handler)
except Exception as e:
	logger.warning(f"Could not set up Logstash handler: {e}")
