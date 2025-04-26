from enum import Enum
from typing import List, Any, Annotated, Optional

import pydantic
from pydantic import BaseModel, Discriminator, Tag, Field as PydanticField


def _schema_field_discriminator(v: Any) -> Optional[str]:
    if isinstance(v, (dict, BaseModel)):
        return "record" if v.get("type") == "RECORD" else "field"
    else:
        return None


class Mode(Enum):
    NULLABLE = "NULLABLE"
    REPEATED = "REPEATED"
    REQUIRED = "REQUIRED"


class TypeEnum(Enum):
    STRING = "STRING"
    BYTES = "BYTES"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    BOOLEAN = "BOOLEAN"
    TIMESTAMP = "TIMESTAMP"
    DATE = "DATE"
    TIME = "TIME"
    DATETIME = "DATETIME"
    GEOGRAPHY = "GEOGRAPHY"
    NUMERIC = "NUMERIC"
    BIGNUMERIC = "BIGNUMERIC"
    JSON = "JSON"
    RECORD = "RECORD"


class Field(BaseModel):
    """
    Cloud Asset Query Field
    See https://cloud.google.com/asset-inventory/docs/reference/rest/v1/TopLevel/queryAssets#TableFieldSchema
    """

    field: str
    mode: Mode = PydanticField(default=Mode.NULLABLE)
    type: TypeEnum


class TableSchema(BaseModel):
    """
    Cloud Asset Query Schema https://cloud.google.com/asset-inventory/docs/reference/rest/v1/TopLevel/queryAssets#TableSchema
    """

    fields: List[
        Annotated[
            (Annotated[Field, Tag("field")] | Annotated["Record", Tag("record")]),
            Discriminator(_schema_field_discriminator),
        ]
    ]


class Record(Field, TableSchema):
    """
    Cloud Asset Query Record Field Type.
    See https://cloud.google.com/asset-inventory/docs/reference/rest/v1/TopLevel/queryAssets#TableFieldSchema
    """

    pass


class QueryResult(BaseModel):
    rows: List[dict]
    table_schema: TableSchema = pydantic.Field(alias="schema")
    next_page_token: Optional[str] = pydantic.Field(alias="nextPageToken")
    total_rows: Optional[int] = pydantic.Field(alias="totalRows")


class AssetQueryResponse(BaseModel):
    done: bool
    job_reference: str = pydantic.Field(alias="jobReference")
    query_result: QueryResult = pydantic.Field(alias="queryResult")
