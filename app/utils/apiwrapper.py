import os
import aiohttp
import asyncio
import traceback

from asyncio import Queue, Task
from aiohttp import TraceConfig
from aiohttp import ClientSession
from typing import TypeVar, Mapping


_T = TypeVar("T")

class ApiWrapper(object):

	_url: str = ""
	_proxy_url: str = ""
	_client_session: ClientSession | None = None
	_trace_configs: list[TraceConfig] = []

	_sleep: float = 0.3

	_queue: Queue | None = None
	_wait_task: Task | None = None

	@staticmethod
	async def create(url: str, rate_limit=None, headers = {}, trace=False) -> 'ApiWrapper':
		api = ApiWrapper()
		return await api.setup(url, rate_limit, headers, trace)

	@classmethod
	async def setup(cls, url: str, rate_limit=None, headers = {}, trace=False):
		if trace:
			async def on_request_end(session, trace_config_ctx, params):
				print("Ending %s request for %s. I sent: %s" % (params.method, params.url, params.headers))
				print('Sent headers: %s' % params.response.request_info.headers)
			trace_config = aiohttp.TraceConfig()
			trace_config.on_request_end.append(on_request_end)
			cls._trace_configs.append(trace_config)
		# formulate the proxy url with authentication
		if (os.environ["proxy_host"] != "") and (os.environ["proxy_host"] is not None):
			proxy_username = os.environ["proxy_username"]
			proxy_password = os.environ["proxy_password"]
			proxy_host = os.environ["proxy_host"]
			proxy_port = os.environ["proxy_port"]
			cls._proxy_url = f"http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}"

		if rate_limit:
			async def wait_task(rate):
				pass
			cls._queue = asyncio.Queue(min(2, int(rate_limit) + 1))
			cls._wait_task = asyncio.create_task(wait_task(rate_limit))

		cls._url = url
		cls._client_session = aiohttp.ClientSession(headers=headers, trace_configs=cls._trace_configs, proxy=cls._proxy_url)
		return cls

	@classmethod
	async def close(cls) -> None:
		await cls._client_session.close()

	@classmethod
	async def get(cls, path: str, headers: Mapping[str, str] = {}) -> str:
		if path != "" or path is not None:
			path = "/".join([cls._url, path])
		try: 
			async with cls._client_session.get(path, headers = headers) as resp:
				if resp.status == 200:
					return await resp.json()
				else:
					print(await resp.text())
					raise Exception(f"Invalid request")
		except Exception as exp:
			print(exp)
			print(traceback.format_exc())

	@classmethod
	async def get_from_url(cls, url: str, headers: Mapping[str, str] = {}) -> str:
		try: 
			async with cls._client_session.get(url, headers = headers) as resp:
				if resp.status == 200:
					return resp.json()
				else:
					print(await resp.text())
					raise Exception(f"Invalid request")
		except Exception as exp:
			print(exp)
			print(traceback.format_exc())


	@classmethod
	async def post(cls, path: str, data: bytes):
		path = "/".join([cls._url, path])
		async with cls._client_session.post(path, data=data) as resp:
			if resp.status == 200:
				return await resp.text()
			else:
				raise Exception("Incorrect data")
