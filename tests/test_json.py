import json
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Iterator

import pytest

from google_asset_query_converter.converter import Converter


@pytest.fixture
def asset_query_result() -> Iterator[dict]:
    test_directory = Path(__file__).resolve().parent
    with test_directory.joinpath("json-query-result.json").open() as f:
        response = json.load(f)
        yield response["queryResult"]


def test_convert_row(asset_query_result: dict):
    expect = [{"json": {"date": "2025-02-12"}}, {"json": {"date": "2025-02-10"}}]
    converter = Converter()
    rows = [r for r in converter.query_result(asset_query_result)]
    assert expect == rows
