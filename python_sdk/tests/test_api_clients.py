import json
from typing import Any, Dict, cast

import httpx
import pytest
import tableauserverclient as TSC
from httpx import Response

from src.api import query_datasource, read_metadata
from src.api.client import VizQLDataServiceClient
from src.api.openapi_generated import (
    Datasource,
    DataType,
    DimensionField,
    Field,
    FieldMetadata,
    MetadataOutput,
    Query,
    QueryOutput,
    QueryRequest,
    ReadMetadataRequest,
)


@pytest.fixture
def mock_server() -> TSC.Server:
    """Create a mock Tableau Server instance"""
    server = TSC.Server("http://localhost")
    # Use _auth_token instead of auth_token as it's a read-only property
    server._auth_token = "mock-token"  # type: ignore
    return server


@pytest.fixture
def mock_auth() -> TSC.TableauAuth:
    """Create a mock Tableau authentication object"""
    return TSC.TableauAuth("test-user", "test-password")


@pytest.fixture
def mock_metadata_response() -> Dict[str, Any]:
    """Mock metadata response"""
    return {
        "data": [
            {
                "fieldName": "Calculation_2278821411780386816",
                "fieldCaption": "Order Profitable?",
                "dataType": "BOOLEAN",
                "logicalTableId": "Migrated Data",
            },
            {
                "fieldName": "Calculation_5571209093911105",
                "fieldCaption": "Profit Ratio",
                "dataType": "REAL",
                "logicalTableId": "",
            },
            {
                "fieldName": "Category",
                "fieldCaption": "Category",
                "dataType": "STRING",
                "logicalTableId": "Migrated Data",
            },
        ]
    }


@pytest.fixture
def mock_query_response() -> Dict[str, Any]:
    """Mock query response"""
    return {
        "data": [
            ["Furniture", 10.459905215419496],
            ["Office Supplies", 32.73404617851419],
            ["Technology", 94.20657260362681],
        ]
    }


@pytest.fixture
def client(
    mock_server: TSC.Server, mock_auth: TSC.TableauAuth
) -> VizQLDataServiceClient:
    """Create a VizQLDataServiceClient instance"""
    return VizQLDataServiceClient("http://localhost", mock_server, mock_auth)


def test_sync_metadata_request(
    client: VizQLDataServiceClient,
    mock_metadata_response: Dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test synchronous metadata request"""

    def mock_request(*args: Any, **kwargs: Any) -> Response:
        return Response(
            status_code=200,
            content=json.dumps(mock_metadata_response).encode(),
            headers={"Content-Type": "application/json"},
        )

    monkeypatch.setattr(httpx.Client, "request", mock_request)

    request = ReadMetadataRequest(
        datasource=Datasource(datasourceLuid="test-datasource")
    )
    response = read_metadata.sync_detailed(client=client, body=request)

    assert response.parsed is not None
    assert isinstance(response.parsed, MetadataOutput)
    data = response.parsed.data
    assert data is not None
    assert len(data) == 3

    # Test first field
    field = cast(FieldMetadata, data[0])
    assert field.fieldName == "Calculation_2278821411780386816"
    assert field.fieldCaption == "Order Profitable?"
    assert field.dataType == DataType.BOOLEAN
    assert field.logicalTableId == "Migrated Data"

    # Test second field
    field = cast(FieldMetadata, data[1])
    assert field.fieldName == "Calculation_5571209093911105"
    assert field.fieldCaption == "Profit Ratio"
    assert field.dataType == DataType.REAL
    assert field.logicalTableId == ""

    # Test third field
    field = cast(FieldMetadata, data[2])
    assert field.fieldName == "Category"
    assert field.fieldCaption == "Category"
    assert field.dataType == DataType.STRING
    assert field.logicalTableId == "Migrated Data"


def test_sync_query_request(
    client: VizQLDataServiceClient,
    mock_query_response: Dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test synchronous query request"""

    def mock_request(*args: Any, **kwargs: Any) -> Response:
        return Response(
            status_code=200,
            content=json.dumps(mock_query_response).encode(),
            headers={"Content-Type": "application/json"},
        )

    monkeypatch.setattr(httpx.Client, "request", mock_request)

    request = QueryRequest(
        datasource=Datasource(datasourceLuid="test-datasource"),
        query=Query(fields=[Field(root=DimensionField(fieldCaption="Category"))]),
    )
    response = query_datasource.sync_detailed(client=client, body=request)

    assert response.parsed is not None
    assert isinstance(response.parsed, QueryOutput)
    data = response.parsed.data
    assert data is not None
    assert len(data) == 3
    assert data[0] == ["Furniture", 10.459905215419496]
    assert data[1] == ["Office Supplies", 32.73404617851419]
    assert data[2] == ["Technology", 94.20657260362681]


@pytest.mark.asyncio
async def test_async_metadata_request(
    client: VizQLDataServiceClient,
    mock_metadata_response: Dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test asynchronous metadata request"""

    async def mock_request(*args: Any, **kwargs: Any) -> Response:
        return Response(
            status_code=200,
            content=json.dumps(mock_metadata_response).encode(),
            headers={"Content-Type": "application/json"},
        )

    monkeypatch.setattr(httpx.AsyncClient, "request", mock_request)

    request = ReadMetadataRequest(
        datasource=Datasource(datasourceLuid="test-datasource")
    )
    response = await read_metadata.asyncio_detailed(client=client, body=request)

    assert response.parsed is not None
    assert isinstance(response.parsed, MetadataOutput)
    data = response.parsed.data
    assert data is not None
    assert len(data) == 3

    # Test first field
    field = cast(FieldMetadata, data[0])
    assert field.fieldName == "Calculation_2278821411780386816"
    assert field.fieldCaption == "Order Profitable?"
    assert field.dataType == DataType.BOOLEAN
    assert field.logicalTableId == "Migrated Data"

    # Test second field
    field = cast(FieldMetadata, data[1])
    assert field.fieldName == "Calculation_5571209093911105"
    assert field.fieldCaption == "Profit Ratio"
    assert field.dataType == DataType.REAL
    assert field.logicalTableId == ""

    # Test third field
    field = cast(FieldMetadata, data[2])
    assert field.fieldName == "Category"
    assert field.fieldCaption == "Category"
    assert field.dataType == DataType.STRING
    assert field.logicalTableId == "Migrated Data"


@pytest.mark.asyncio
async def test_async_query_request(
    client: VizQLDataServiceClient,
    mock_query_response: Dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test asynchronous query request"""

    async def mock_request(*args: Any, **kwargs: Any) -> Response:
        return Response(
            status_code=200,
            content=json.dumps(mock_query_response).encode(),
            headers={"Content-Type": "application/json"},
        )

    monkeypatch.setattr(httpx.AsyncClient, "request", mock_request)

    request = QueryRequest(
        datasource=Datasource(datasourceLuid="test-datasource"),
        query=Query(fields=[Field(root=DimensionField(fieldCaption="Category"))]),
    )
    response = await query_datasource.asyncio_detailed(client=client, body=request)

    assert response.parsed is not None
    assert isinstance(response.parsed, QueryOutput)
    data = response.parsed.data
    assert data is not None
    assert len(data) == 3
    assert data[0] == ["Furniture", 10.459905215419496]
    assert data[1] == ["Office Supplies", 32.73404617851419]
    assert data[2] == ["Technology", 94.20657260362681]


def test_sync_workbook_datasource_query_request(
    mock_server: TSC.Server,
    mock_auth: TSC.TableauAuth,
    mock_query_response: Dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When the workbook header kwargs are supplied to the constructor, the
    resulting client sends Global-Session-Header and X-Session-Id on the wire."""
    captured: Dict[str, Any] = {}

    def mock_request(self: httpx.Client, *args: Any, **kwargs: Any) -> Response:
        captured["headers"] = dict(self.headers)
        return Response(
            status_code=200,
            content=json.dumps(mock_query_response).encode(),
            headers={"Content-Type": "application/json"},
        )

    monkeypatch.setattr(httpx.Client, "request", mock_request)

    workbook_client = VizQLDataServiceClient(
        "http://localhost",
        mock_server,
        mock_auth,
        global_session_header="gsh",
        x_session_id="sid",
    )
    request = QueryRequest(
        datasource=Datasource(workbookDatasourceId="wb-ds-abc"),
        query=Query(fields=[Field(root=DimensionField(fieldCaption="Category"))]),
    )
    query_datasource.sync_detailed(client=workbook_client, body=request)

    assert captured["headers"]["global-session-header"] == "gsh"
    assert captured["headers"]["x-session-id"] == "sid"


@pytest.mark.asyncio
async def test_async_workbook_datasource_query_request(
    mock_server: TSC.Server,
    mock_auth: TSC.TableauAuth,
    mock_query_response: Dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Same as the sync workbook test, but for the async dispatcher."""
    captured: Dict[str, Any] = {}

    async def mock_request(
        self: httpx.AsyncClient, *args: Any, **kwargs: Any
    ) -> Response:
        captured["headers"] = dict(self.headers)
        return Response(
            status_code=200,
            content=json.dumps(mock_query_response).encode(),
            headers={"Content-Type": "application/json"},
        )

    monkeypatch.setattr(httpx.AsyncClient, "request", mock_request)

    workbook_client = VizQLDataServiceClient(
        "http://localhost",
        mock_server,
        mock_auth,
        global_session_header="gsh",
        x_session_id="sid",
    )
    request = QueryRequest(
        datasource=Datasource(workbookDatasourceId="wb-ds-async"),
        query=Query(fields=[Field(root=DimensionField(fieldCaption="Category"))]),
    )
    await query_datasource.asyncio_detailed(client=workbook_client, body=request)

    assert captured["headers"]["global-session-header"] == "gsh"
    assert captured["headers"]["x-session-id"] == "sid"


def test_client_ignores_session_headers_when_incomplete(
    mock_server: TSC.Server,
    mock_auth: TSC.TableauAuth,
) -> None:
    """When only one of the two workbook header params is supplied, the
    constructor must not attach any workbook header."""
    partial_client = VizQLDataServiceClient(
        "http://localhost",
        mock_server,
        mock_auth,
        global_session_header="gsh",
    )
    headers = partial_client.get_httpx_client().headers
    assert "global-session-header" not in headers
    assert "x-session-id" not in headers
