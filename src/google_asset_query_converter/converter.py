import base64
from datetime import datetime, date, time, UTC
from typing import Any, Optional, Dict, Callable, Iterator
import json
from decimal import Decimal

from google_asset_query_converter.queryresult import (
    TableSchema,
    TypeEnum,
    Field,
    Mode,
    Record,
)


PYTHON_NATIVE_CONVERTERS: Dict[TypeEnum, Callable[[str], Optional[Any]]] = {
    TypeEnum.STRING: lambda v: v,
    TypeEnum.BYTES: lambda v: base64.b64decode(v) if v else None,
    TypeEnum.INTEGER: lambda v: int(v) if v is not None else None,
    TypeEnum.FLOAT: lambda v: float(v) if v is not None else None,
    TypeEnum.BOOLEAN: lambda v: v == "true" if v else None,
    TypeEnum.TIMESTAMP: lambda v: datetime.fromtimestamp(float(v), UTC) if v else None,
    TypeEnum.DATE: lambda v: date.fromisoformat(v) if v else None,
    TypeEnum.TIME: lambda v: time.fromisoformat(v) if v else None,
    TypeEnum.DATETIME: lambda v: datetime.fromtimestamp(v, UTC) if v else None,
    TypeEnum.GEOGRAPHY: lambda v: v,
    TypeEnum.NUMERIC: lambda v: Decimal(v) if v else None,
    TypeEnum.BIGNUMERIC: lambda v: Decimal(v) if v else None,
    TypeEnum.JSON: lambda v: json.loads(v) if v else None,
}

JSON_NATIVE_CONVERTERS: Dict[TypeEnum, Callable[[str], Optional[Any]]] = {
    TypeEnum.STRING: lambda v: v,
    TypeEnum.BYTES: lambda v: v,
    TypeEnum.INTEGER: lambda v: int(v) if v is not None else None,
    TypeEnum.FLOAT: lambda v: float(v) if v is not None else None,
    TypeEnum.BOOLEAN: lambda v: v == "true" if v else None,
    TypeEnum.TIMESTAMP: lambda v: v,
    TypeEnum.DATE: lambda v: v,
    TypeEnum.TIME: lambda v: v,
    TypeEnum.DATETIME: lambda v: v,
    TypeEnum.GEOGRAPHY: lambda v: v,
    TypeEnum.NUMERIC: lambda v: v,
    TypeEnum.BIGNUMERIC: lambda v: v,
    TypeEnum.JSON: lambda v: json.loads(v) if v else None,
}

class Converter:
    """
    Converts Cloud Asset Query results to Python native types.
    """

    _converters: Dict[TypeEnum, Callable[[str], Optional[Any]]]

    def __init__(
        self,
        converters: Optional[Dict[TypeEnum, Callable[[str], Optional[Any]]]] = None,
    ):
        """
        Initializes the converters with a converter for specified field types. If no converter is given,
        for a specified type, the value will be returned as is.

        If no converters are given, the default `PYTHON_NATIVE_CONVERTERS` will be used. To
        serialize to JSON, use `JSON_NATIVE_CONVERTERS` instead. To maintain all string values
        specify an empty dictionary.

        """
        self._converters = converters if converters else PYTHON_NATIVE_CONVERTERS

    @property
    def converters(self) -> Dict[TypeEnum, Callable[[str], Optional[Any]]]:
        return self._converters

    def _value_to_dict(
        self, field: Field, value: Optional[list | dict]
    ) -> Optional[Any]:
        """
        converts the value conforming to the field definition to a python value or a list of python values
        if it is an REPEATED field type.

        The Cloud Asset Query result returns all values as JSON strings. The string value is
        converted to a corresponding native type using a converter from self.converters.
        """
        if field.mode == Mode.REPEATED and isinstance(value["v"], list):
            return [self._value_to_dict(field, v) for v in value["v"]]

        return self._converters.get(field.type, lambda v: v)(value["v"])

    def _record_to_dict(
        self, record: Record, value: Optional[list | dict]
    ) -> Optional[Any]:
        """
        converts the value conforming to the record definition to a python object or a list of python objects
        if it is an REPEATED field type.
        """
        if not (record_value := value["v"]):
            return None

        if record.mode == Mode.REPEATED and isinstance(record_value, list):
            return [self._record_to_dict(record, v) for v in record_value]

        return {
            field.field: self._field_to_dict(field, record_value["f"][i])
            for i, field in enumerate(record.fields)
        }

    def _field_to_dict(
        self, field: Field | Record, value: Optional[list | dict]
    ) -> Optional[Any]:
        """
        converts the value conforming to the field definition to a python value.
        """
        if isinstance(field, Record):
            return self._record_to_dict(field, value)
        else:
            return self._value_to_dict(field, value)

    def row(self, schema: TableSchema, row: dict) -> dict:
        """
        converts a cloud asset query result row conforming to the schema to a python object.
        """
        assert "f" in row
        return {
            field.field: self._field_to_dict(field, row["f"][i])
            for i, field in enumerate(schema.fields)
        }

    def query_result(self, query_result: dict) -> Iterator[dict]:
        """
        converts each row in the query result to a python object.
        """
        schema = TableSchema(**query_result["schema"])
        for row in query_result.get("rows", []):
            yield self.row(schema, row)


class PythonConverter(Converter):
    """
    converts Cloud Asset Query results to Python native types.
    """
    def __init__(self):
        super().__init__(PYTHON_NATIVE_CONVERTERS)


class JSONConverter(Converter):
    """
    converts Cloud Asset Query results to JSON native types.
    """
    def __init__(self):
        super().__init__(JSON_NATIVE_CONVERTERS)
