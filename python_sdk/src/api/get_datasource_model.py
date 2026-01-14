from http import HTTPStatus
from typing import Any, Optional

import httpx

from .client import VizQLDataServiceClient
from .errors import UnexpectedStatus
from .openapi_generated import DatasourceModelOutput, GetDatasourceModelRequest
from .types import Response


def _get_kwargs(
    *,
    body: GetDatasourceModelRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/get-datasource-model",
    }

    _body = body.model_dump(mode="json", exclude_none=True)
    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: VizQLDataServiceClient, response: httpx.Response
) -> Optional[DatasourceModelOutput]:
    if response.status_code == 200:
        response_200 = DatasourceModelOutput.model_validate_json(response.content)

        return response_200
    if client.raise_on_unexpected_status:
        raise UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: VizQLDataServiceClient, response: httpx.Response
) -> Response[DatasourceModelOutput]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: VizQLDataServiceClient,
    body: GetDatasourceModelRequest,
) -> Response[DatasourceModelOutput]:
    """Request data source model with detailed response information

    Requests the data model for a specific data source and returns a detailed response containing:
    - The data source model (`DatasourceModelOutput`)
    - HTTP status code
    - Response headers
    - Raw response content

    Args:
        body (GetDatasourceModelRequest): The data source model request parameters.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DatasourceModelOutput]: A response object containing both the data source model and response metadata.
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: VizQLDataServiceClient,
    body: GetDatasourceModelRequest,
) -> Optional[DatasourceModelOutput]:
    """Request data source model and get only the model information

    Requests the data model for a specific data source and returns only the model information without response metadata.
    This is a convenience wrapper around sync_detailed() that returns only the parsed model.

    Args:
        body (GetDatasourceModelRequest): The data source model request parameters.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Optional[DatasourceModelOutput]: The data source model, or None if the request was unsuccessful.
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: VizQLDataServiceClient,
    body: GetDatasourceModelRequest,
) -> Response[DatasourceModelOutput]:
    """Request data source model asynchronously with detailed response information

    Asynchronously requests the data model for a specific data source and returns a detailed response containing:
    - The data source model (`DatasourceModelOutput`)
    - HTTP status code
    - Response headers
    - Raw response content

    Args:
        body (GetDatasourceModelRequest): The data source model request parameters.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DatasourceModelOutput]: A response object containing both the data source model and response metadata.
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: VizQLDataServiceClient,
    body: GetDatasourceModelRequest,
) -> Optional[DatasourceModelOutput]:
    """Request data source model asynchronously and get only the model information

    Asynchronously requests the data model for a specific data source and returns only the model information without response metadata.
    This is a convenience wrapper around asyncio_detailed() that returns only the parsed model.

    Args:
        body (GetDatasourceModelRequest): The data source model request parameters.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Optional[DatasourceModelOutput]: The data source model, or None if the request was unsuccessful.
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed


__all__ = [
    "sync",
    "sync_detailed",
    "asyncio",
    "asyncio_detailed",
]
