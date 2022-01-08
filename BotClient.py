from HTTPClient import HTTPClient, ClientType, Route
from typing import Any


class BotClient(HTTPClient):

	def __init__(self, token: str):
		super().__init__()
		self.token = token

	def getHeaders(self):

		headers = {
			"Authorization": f"Bot {self.token}"
		}
		headers.update(super().getHeaders())
		return headers

	def request(self, route: Route, headers: dict={}, data: Any=None, payload: Any=None):
		h = self.getHeaders()
		h.update(headers)
		return super().request(route, h, data, payload)