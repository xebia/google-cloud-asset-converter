import base64
import json
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Iterator

import pytest

from google_asset_query_converter.converter import (
    PYTHON_NATIVE_CONVERTERS,
    JSON_NATIVE_CONVERTERS,
)
from google_asset_query_converter.queryresult import TypeEnum


def test_python_native_converters_is_complete():
    assert set(PYTHON_NATIVE_CONVERTERS.keys()) == (set(TypeEnum) - {TypeEnum.RECORD})


def test_json_native_converters_is_complete():
    assert set(JSON_NATIVE_CONVERTERS.keys()) == (set(TypeEnum) - {TypeEnum.RECORD})
