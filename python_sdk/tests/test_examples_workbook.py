"""End-to-end-ish tests that drive sync_examples.execute and
async_examples.execute, asserting the workbook code path is gated on the
three required CLI args and dispatches every WORKBOOK_QUERY_FUNCTIONS entry
with a workbookDatasourceId-based QueryRequest and the right headers.

Network and Tableau sign-in are monkeypatched so these stay unit-test cheap.
"""

import argparse
import asyncio
from contextlib import contextmanager
from unittest.mock import MagicMock

import pytest

from src.api import get_datasource_model, query_datasource, read_metadata
from src.examples import async_examples, common, sync_examples
from src.examples.payload import WORKBOOK_QUERY_FUNCTIONS


def _full_args(**overrides):
    base = dict(
        server="https://example.tableau.test",
        user="u",
        password="p",
        pat_name=None,
        pat_secret=None,
        jwt_token=None,
        site="",
        verbose=False,
        workbook_datasource_id=None,
        global_session_header=None,
        x_session_id=None,
    )
    base.update(overrides)
    return argparse.Namespace(**base)


@contextmanager
def _patched_runtime(monkeypatch):
    """Stub out network/auth so execute() can run without a real server."""
    fake_server = MagicMock(name="TSC.Server")
    fake_server.auth.sign_in.return_value.__enter__ = lambda self: None
    fake_server.auth.sign_in.return_value.__exit__ = (
        lambda self, exc_type, exc, tb: None
    )

    monkeypatch.setattr(
        "tableauserverclient.Server",
        MagicMock(return_value=fake_server),
        raising=True,
    )
    monkeypatch.setattr(common, "create_server", lambda **_kw: ("https://x", object()))
    monkeypatch.setattr(
        common,
        "list_datasources_and_get_luid",
        lambda server, verbose=False: "ds-luid-1",
    )

    fake_client = MagicMock(name="VizQLDataServiceClient")
    monkeypatch.setattr(
        sync_examples, "VizQLDataServiceClient", lambda *a, **kw: fake_client
    )
    monkeypatch.setattr(
        async_examples, "VizQLDataServiceClient", lambda *a, **kw: fake_client
    )

    sync_calls = {"query": [], "metadata": [], "model": [], "with_headers": []}

    def fake_sync_detailed(*, client, body):
        sync_calls["query"].append((client, body))
        return MagicMock(status_code=200, headers={}, content=b"{}")

    def fake_metadata(*, client, body):
        sync_calls["metadata"].append((client, body))
        return MagicMock(status_code=200, headers={}, content=b"{}")

    def fake_model(*, client, body):
        sync_calls["model"].append((client, body))
        return MagicMock(status_code=200, headers={}, content=b"{}")

    async def fake_async_detailed(*, client, body):
        sync_calls["query"].append((client, body))
        return MagicMock(status_code=200, headers={}, content=b"{}")

    async def fake_async_metadata(*, client, body):
        sync_calls["metadata"].append((client, body))
        return MagicMock(status_code=200, headers={}, content=b"{}")

    async def fake_async_model(*, client, body):
        sync_calls["model"].append((client, body))
        return MagicMock(status_code=200, headers={}, content=b"{}")

    monkeypatch.setattr(query_datasource, "sync_detailed", fake_sync_detailed)
    monkeypatch.setattr(query_datasource, "asyncio_detailed", fake_async_detailed)
    monkeypatch.setattr(read_metadata, "sync_detailed", fake_metadata)
    monkeypatch.setattr(read_metadata, "asyncio_detailed", fake_async_metadata)
    monkeypatch.setattr(get_datasource_model, "sync_detailed", fake_model)
    monkeypatch.setattr(get_datasource_model, "asyncio_detailed", fake_async_model)

    workbook_client = MagicMock(name="WorkbookClient")
    fake_client.with_headers.side_effect = lambda headers: (
        sync_calls["with_headers"].append(headers) or workbook_client
    )

    yield sync_calls, fake_client, workbook_client


def _workbook_query_calls(sync_calls, workbook_client):
    """All query_datasource.* calls that were dispatched on the workbook
    (with_headers) client. Identifies workbook calls by `client is`."""
    return [body for client, body in sync_calls["query"] if client is workbook_client]


def test_sync_examples_skips_workbook_path_when_args_missing(monkeypatch):
    with _patched_runtime(monkeypatch) as (sync_calls, _client, _wb_client):
        sync_examples.execute(_full_args())
    assert sync_calls["with_headers"] == []
    # Every query_datasource call should have been on the LUID client.
    assert all(
        b.datasource.datasourceLuid == "ds-luid-1"
        for b in [body for _c, body in sync_calls["query"]]
    )


def test_sync_examples_runs_workbook_path_when_all_args_present(monkeypatch):
    args = _full_args(
        workbook_datasource_id="wb-ds-7",
        global_session_header="gsh-value",
        x_session_id="sid-value",
    )
    with _patched_runtime(monkeypatch) as (sync_calls, _client, workbook_client):
        sync_examples.execute(args)

    # with_headers was called exactly once with the two documented headers.
    assert sync_calls["with_headers"] == [
        {"Global-Session-Header": "gsh-value", "X-Session-Id": "sid-value"}
    ]

    workbook_bodies = _workbook_query_calls(sync_calls, workbook_client)
    assert len(workbook_bodies) == len(WORKBOOK_QUERY_FUNCTIONS)
    for body in workbook_bodies:
        assert body.datasource.workbookDatasourceId == "wb-ds-7"
        assert body.datasource.datasourceLuid is None


def test_async_examples_skips_workbook_path_when_args_missing(monkeypatch):
    with _patched_runtime(monkeypatch) as (sync_calls, _client, _wb_client):
        asyncio.run(async_examples.execute(_full_args()))
    assert sync_calls["with_headers"] == []


def test_async_examples_runs_workbook_path_when_all_args_present(monkeypatch):
    args = _full_args(
        workbook_datasource_id="wb-ds-async",
        global_session_header="gsh-a",
        x_session_id="sid-a",
    )
    with _patched_runtime(monkeypatch) as (sync_calls, _client, workbook_client):
        asyncio.run(async_examples.execute(args))

    assert sync_calls["with_headers"] == [
        {"Global-Session-Header": "gsh-a", "X-Session-Id": "sid-a"}
    ]
    workbook_bodies = _workbook_query_calls(sync_calls, workbook_client)
    assert len(workbook_bodies) == len(WORKBOOK_QUERY_FUNCTIONS)
    for body in workbook_bodies:
        assert body.datasource.workbookDatasourceId == "wb-ds-async"
        assert body.datasource.datasourceLuid is None


@pytest.mark.parametrize(
    "missing_kwargs",
    [
        {"workbook_datasource_id": "x", "global_session_header": "y"},
        {"workbook_datasource_id": "x", "x_session_id": "z"},
        {"global_session_header": "y", "x_session_id": "z"},
        {
            "workbook_datasource_id": "x",
            "global_session_header": "  ",
            "x_session_id": "z",
        },
    ],
)
def test_sync_examples_workbook_path_requires_all_three_args(
    monkeypatch, missing_kwargs
):
    with _patched_runtime(monkeypatch) as (sync_calls, _client, _wb_client):
        sync_examples.execute(_full_args(**missing_kwargs))
    assert sync_calls["with_headers"] == []
