import json
from enum import Enum
from pathlib import Path
from typing import Iterator

import pytest

from google_asset_query_converter.converter import Converter
from google_asset_query_converter.schema import TableSchema


@pytest.fixture
def assert_query_result() -> Iterator[dict]:
    test_directory = Path(__file__).resolve().parent
    with test_directory.joinpath("query-result.json").open() as f:
        response = json.load(f)
        yield response["queryResult"]


def test_load_schema(assert_query_result: dict):
    schema = TableSchema(**assert_query_result["schema"])

    class EnumEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Enum):
                return obj.name
            return json.JSONEncoder.default(self, obj)

    rounded_tripped = json.loads(json.dumps(schema.model_dump(), cls=EnumEncoder))
    assert assert_query_result["schema"] == rounded_tripped


def test_convert_row(assert_query_result: dict):
    row = assert_query_result["rows"][0]
    schema = TableSchema(**assert_query_result["schema"])
    converter = Converter()
    c = converter.row(schema, row)
