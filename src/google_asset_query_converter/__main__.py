import sys
import json
import argparse

from google_asset_query_converter.converter import JSONConverter
from google_asset_query_converter.queryresult import AssetQueryResponse


def main():
    """
    Convert Google Asset Query results to JSON.

    The gcloud asset query command returns the result in a custom format consisting of fields named f and v.
    this utility converts it to proper JSON by interpreting the schema returned with the results.

    Usage:
       gcloud asset query \
          --format=json \
          --statement 'select * from compute_googleapis_com' | \
       google-asset-query-converter

    """
    parser = argparse.ArgumentParser(description="Convert Google Asset Query results to JSON")
    parser.add_argument("--pretty-print", action="store_true", help="Pretty print the JSON output")
    args = parser.parse_args()

    convert = JSONConverter()
    data = sys.stdin.read()
    response = AssetQueryResponse.model_validate_json(data)
    query_result = response.query_result
    json.dump(
        list(
            map(lambda r: convert.row(query_result.table_schema, r), query_result.rows)
        ),
        sys.stdout,
        indent=2 if args.pretty_print else None,
    )


if __name__ == "__main__":
    main()
