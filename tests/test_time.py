import json
from datetime import time
from enum import Enum
from pathlib import Path
from typing import Iterator

import pytest

from google_asset_query_converter.converter import Converter


@pytest.fixture
def asset_query_result() -> Iterator[dict]:
    test_directory = Path(__file__).resolve().parent
    with test_directory.joinpath("time-query-result.json").open() as f:
        response = json.load(f)
        yield response["queryResult"]


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.name
        elif isinstance(obj, time):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


def test_convert_row(asset_query_result: dict):
    expect = [{"time": time(12, 7, 35, 919282)}, {"time": time(0, 8, 29, 564838)}]
    converter = Converter()
    rows = [r for r in converter.query_result(asset_query_result)]
    assert expect == rows
