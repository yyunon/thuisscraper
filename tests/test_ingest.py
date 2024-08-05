# test_module.py

import json
import unittest
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ingest.scraper import Scraper
from app.utils.apiwrapper import ApiWrapper
from app.database.engine import DbWrapper


@pytest.mark.asyncio
async def test_geo_locate():

    scraper = Scraper(None)

    class MockApi(object):
        async def get(cls, *args, **kwargs):
            return json.loads(json.dumps({"addresses": [{"lat": 1, "lng": 2, "deliveryAreaId": 12, "takeawayPostalCode": "1014"},{"lat": 1, "lng": 2, "deliveryAreaId": 12, "takeawayPostalCode": "1015"}]}))

    scraper._api_wrapper = MockApi

    res = await scraper.geo_locate("addr")

    assert res == (1,2,12,"1014")
    assert res != (1,2,12,"1015")

if __name__ == '__main__':
    unittest.main()