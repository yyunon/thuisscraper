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
		'X-Language-Code': 'nl',
		'X-Country-Code': 'nl',
		'X-Session-ID': '953dc443-f124-4dbb-b0bc-d4e6c3be4703',
		'X-Requested-With': 'XMLHttpRequest',
		'x-datadog-origin': 'rum',
		'x-datadog-parent-id': '7120459953290521979',
		'x-datadog-sampling-priority': '1',
		'x-datadog-trace-id': '3091576322640470315',
	}
