google-asset-query-converter
============================
Converts the output of a Google Asset Query result into a JSON or a native Python object. It can be used
as a command line filter for gcloud or as a library in a Python program.

## Command Line Usage
When using gcloud asset query on the command line, the result is outputted in a table format:

```shell
gcloud asset query \
    --project $(gcloud config get core/project) \
    --statement 'select distinct(assetType) as type from STANDARD_METADATA'
```

```text
done: true
jobReference: CiBqb2JfTmZaRzdQcTNXdHRaRi1OOFVUZWFPYnQyVW53QxIBDRiKrf2fpr6_t9cB
queryResult:
  nextPageToken: ''
  totalRows: '43'

┌─────────────────────────────────────────────────┐
│                       type                      │
├─────────────────────────────────────────────────┤
│ dataplex.googleapis.com/EntryGroup              │
│ containerregistry.googleapis.com/Image          │
...
```

This is not very useful. For most CLI usages JSON would be handier. Unfortunately the JSON and YAML output
of the query command is not what you expect. It looks like this:

```shell
gcloud asset query \
    --project $(gcloud config get core/project) \
    --format json \
    --statement 'select distinct(assetType) as type from STANDARD_METADATA'
```

```json
{
  "queryResult": {
    "nextPageToken": "",
    "rows": [
      {
        "f": [
          {
            "v": "compute.googleapis.com/Network"
          }
        ]
      },
      {
        "f": [
          {
            "v": "secretmanager.googleapis.com/SecretVersion"
          }
        ]
      }
      ...
    ],
    "schema": {
      "fields": [
        {
          "field": "type",
          "mode": "NULLABLE",
          "type": "STRING"
        }
      ]
    },
    "totalRows": "43"
  }
```

This utility use the schema definition that is returned with the result, to provide a proper JSON:

```shell
gcloud asset query \
    --project $(gcloud config get core/project) \
    --format json \
    --statement 'select distinct(assetType) as type from STANDARD_METADATA' | \
    google-asset-query-converter --pretty-print
```

```json
[
  {
    "type": "compute.googleapis.com/InstanceGroup"
  },
  {
    "type": "appengine.googleapis.com/Application"
  },
  {
    ..
  ]
```

Now it is easier to process the query results without tools like 'jq':

```shell
gcloud asset query \
    --project $(gcloud config get core/project) \
    --format json \
    --statement 'select distinct(assetType) as type from STANDARD_METADATA' | \
    google-asset-query-converter --pretty-print | \
    jq 'map(.type)'
```

```json
[
  "appengine.googleapis.com/Application",
  "compute.googleapis.com/InstanceGroup",
  "pubsub.googleapis.com/Topic",
  "iam.googleapis.com/ServiceAccount",
  "compute.googleapis.com/Disk",
  "bigquery.googleapis.com/Table",
  ...
```

For this simple query you could have processed the output directly from the query, but I dear you to process the
output  of `select * from compute_googleapis_com_Instance` directly with jq :-p

## Library Usage
You can also use the converter to process the results of a cloud asset query in Python.

```python
from googleapiclient.discovery import build
from google_asset_query_converter.converter import PythonConverter
from google_asset_query_converter.queryresult import AssetQueryResponse


def print_metadata(project:str):
    service = build("cloudasset", "v1")
    request = service.v1().queryAssets(
        parent=f'projects/{project}',
        body={"statement":  "SELECT * FROM STANDARD_METADATA",
              "pageSize": 20
              }
    )

    converter = PythonConverter()
    response = AssetQueryResponse(**request.execute())
    for row in response.query_result.rows:
        print(converter.row(response.query_result.table_schema, row))
```

## Installation

To install this utility library, type:

```shell
pip install git+https://github.com/xebia/google-asset-query-converter.git@0.0.3
```

It required Python 3.12 or later.
