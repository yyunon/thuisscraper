import os
import json
import urllib
import aiohttp

import traceback
from aiohttp import ClientSession
from typing import TypeVar, Mapping, Callable, Any

_T = TypeVar("T")


class ApiWrapper(object):

	_url: str = ""
	_proxy_url: str = ""
	_client_session: ClientSession | None = None

	def __init__(self, url: str):
		self.setup(url)

	@classmethod
	def setup(cls, url: str, useProxy: bool = False):
		# formulate the proxy url with authentication
		if useProxy:
			proxy_username = os.environ["proxy_username"]
			proxy_password = os.environ["proxy_password"]
			proxy_host = os.environ["proxy_host"]
			proxy_port = os.environ["proxy_port"]
			cls._proxy_url = f"http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}"
		cls._url = url
		print(f"Setting up client {cls._url}")
		cls._client_session = aiohttp.ClientSession()

	@classmethod
	async def close(cls) -> None:
		await cls._client_session.close()

	@classmethod
	async def get(cls, path: str, headers: Mapping[str, str] = {}, parse_func: Callable | None = None) -> Any:
		if path != "" or path is not None:
			path = "/".join([cls._url, path])
		print(f"Getting path {path}")
		try: 
			async with cls._client_session.get(path, headers = headers) as resp:
				print(resp.status)
				if resp.status == 200:
					#if parse_func is not None:
					#	for r in await resp.json():
					#		yield parse_func(r)
					#else:
					return await resp.json()
				else:
					print(await resp.text())
					raise Exception(f"Invalid request")
		except Exception as exp:
			print(exp)
			print(traceback.format_exc())
