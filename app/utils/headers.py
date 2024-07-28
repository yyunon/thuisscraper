from fake_useragent import UserAgent

def generate_header() -> dict:
	ua = UserAgent()
	return {
		'User-Agent': ua.random,
		'Accept': 'application/json, text/plain, */*',
		'Accept-Encoding': 'gzip, deflate, br, zstd',
		'Accept-Language': 'nl',
		'Cache-Control': 'no-cache',
		'Connection': 'keep-alive',
		'Host': 'cw-api.takeaway.com',
		'Origin': 'https://www.thuisbezorgd.nl',
		'Referer': 'https://www.thuisbezorgd.nl',
		'Sec-Fetch-Dest':'empty',
		'Sec-Fetch-Mode':'cors',
		'Sec-Fetch-Site':'cross-site',
	}
