import pytest
from googleapiclient.discovery import build
from google_asset_query_converter.converter import PythonConverter
from google_asset_query_converter.queryresult import AssetQueryResponse
import gcloud_config_helper


@pytest.mark.integration_test
def test_execute_asset_query_with_discovery():

    credentials, project = gcloud_config_helper.default()
    service = build("cloudasset", "v1", credentials=credentials)
    request = service.v1().queryAssets(
        parent=f"projects/{project}",
        body={"statement": "SELECT * FROM STANDARD_METADATA", "pageSize": 20},
    )

    converter = PythonConverter()
    while True:
        response = AssetQueryResponse(**request.execute())
        for row in response.query_result.rows:
            print(converter.row(response.query_result.table_schema, row))
        if not response.query_result.next_page_token:
            return

        request = service.v1().queryAssets(
            parent=f"projects/{project}",
            body={
                "pageToken": response.query_result.next_page_token,
                "jobReference": response.job_reference,
            },
        )


if __name__ == "__main__":
    test_execute_asset_query_with_discovery()
