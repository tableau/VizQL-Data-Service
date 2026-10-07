import argparse
import inspect
import os
import sys
import traceback
from typing import Iterable, Optional, Union

import tableauserverclient as TSC

# Add project root to sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, root_dir)

# Determine if we're in development or production environment
is_development = os.path.basename(root_dir) == "python_sdk"

if is_development:
    from src.api import (
        get_datasource_model,
        query_datasource,
        read_metadata,
    )
    from src.api.client import VizQLDataServiceClient
    from src.api.constants import (
        SAMPLE_DATASOURCE,
        SAMPLE_STATIC_WORKBOOK_DATASOURCE,
        SAMPLE_WORKBOOK,
    )
    from src.api.openapi_generated import (
        Datasource,
        GetDatasourceModelRequest,
        QueryRequest,
        ReadMetadataRequest,
    )
    from src.api.utils import format_server_url
    from src.examples.payload import QUERY_FUNCTIONS
else:
    from vizql_data_service_py.api import (  # type: ignore
        get_datasource_model,
        query_datasource,
        read_metadata,
    )
    from vizql_data_service_py.api.client import VizQLDataServiceClient  # type: ignore
    from vizql_data_service_py.api.constants import (  # type: ignore
        SAMPLE_DATASOURCE,
        SAMPLE_STATIC_WORKBOOK_DATASOURCE,
        SAMPLE_WORKBOOK,
    )
    from vizql_data_service_py.api.openapi_generated import (  # type: ignore
        Datasource,
        GetDatasourceModelRequest,
        QueryRequest,
        ReadMetadataRequest,
    )
    from vizql_data_service_py.api.utils import format_server_url  # type: ignore
    from vizql_data_service_py.examples.payload import (  # type: ignore
        QUERY_FUNCTIONS,
    )


def print_help():
    """Print help information for all available commands."""
    print("\n=== VizQL Data Service Python SDK Examples ===")
    print("\nBasic Usage:")
    print("  python examples.py [options]")
    print("  python examples.py --async [options]  # Run in async mode")

    print("\nRequired Arguments:")
    print("  -s, --server URL    Tableau Server URL (required)")

    print("\nAuthentication Options (choose one authentication):")
    print("  -u, --user USERNAME        Tableau Server username")
    print("  -p, --password PASSWORD    Tableau Server password")
    print("  -n, --pat-name NAME        Personal Access Token name")
    print("  -t, --pat-secret SECRET    Personal Access Token secret")
    print("  -j, --jwt-token TOKEN      JWT token")

    print("\nOptional Arguments:")
    print(
        "  -S, --site SITE_NAME       Tableau Server site name, or the default site if unspecified"
    )
    print("  -v, --verbose              Print detailed request response information")
    print(
        "  --no-verify-ssl            Disable SSL certificate verification (test hosts only)"
    )
    print("  -h, --help                 Show this help message")
    print(
        "  --workbook-datasource-id ID  Run additional queries against a workbook datasource"
    )
    print(
        "  --global-session-header V    Value for the 'Global-Session-Header' request header"
    )
    print("  --x-session-id V             Value for the 'X-Session-Id' request header")

    print("\nExamples:")
    print("  1. Basic usage with username/password:")
    print("     python examples.py -s https://your-server -u admin -p password")
    print("\n  2. Using Personal Access Token:")
    print(
        "     python examples.py -s https://your-server -n token-name -t token-secret"
    )
    print("\n  3. Using JWT token:")
    print("     python examples.py -s https://your-server -j your-jwt-token")
    print("\n  4. Running in async mode with verbose output:")
    print(
        "     python examples.py --async -v -s https://your-server -u admin -p password"
    )


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="VizQL Data Service Python SDK Examples",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,  # Disable default help
    )
    parser.add_argument("-s", "--server", required=True, help="Tableau Server URL")
    parser.add_argument("-u", "--user", help="Tableau Server username")
    parser.add_argument("-p", "--password", help="Tableau Server password")
    parser.add_argument("-n", "--pat-name", help="Personal Access Token name")
    parser.add_argument("-t", "--pat-secret", help="Personal Access Token secret")
    parser.add_argument("-j", "--jwt-token", help="JWT token")
    parser.add_argument("-S", "--site", help="Tableau Server site name")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Print detailed information"
    )
    parser.add_argument(
        "--no-verify-ssl",
        dest="no_verify_ssl",
        action="store_true",
        help=(
            "Disable SSL certificate verification. Use for internal test "
            "servers whose certificate chain your local trust store cannot "
            "validate. Do not use against production servers."
        ),
    )
    parser.add_argument(
        "-h", "--help", action="store_true", help="Show this help message"
    )
    parser.add_argument(
        "--workbook-datasource-id",
        dest="workbook_datasource_id",
        help=(
            "Workbook datasource id used to run an additional set of queries "
            "against a workbook datasource. Requires --global-session-header "
            "and --x-session-id."
        ),
    )
    parser.add_argument(
        "--global-session-header",
        dest="global_session_header",
        help=(
            "Value sent in the 'Global-Session-Header' request header for "
            "workbook-datasource-id queries. Requires --workbook-datasource-id "
            "and --x-session-id."
        ),
    )
    parser.add_argument(
        "--x-session-id",
        dest="x_session_id",
        help=(
            "Value sent in the 'X-Session-Id' request header for "
            "workbook-datasource-id queries. Requires --workbook-datasource-id "
            "and --global-session-header."
        ),
    )
    return parser


def list_datasources_and_get_luid(server: TSC.Server, verbose: bool = False):
    if not server.auth_token:
        raise RuntimeError("Not signed in. Please call sign_in() first.")
    all_datasources, pagination_item = server.datasources.get()

    if verbose:
        print(f"\nThere are {pagination_item.total_available} datasources on site:")
        for ds in all_datasources:
            print(f"- {ds.name} (LUID: {ds.id})")

    matching_datasources = [
        ds for ds in all_datasources if ds.name == SAMPLE_DATASOURCE
    ]
    if not matching_datasources:
        raise ValueError(f"Datasource named '{SAMPLE_DATASOURCE}' not found.")

    selected_ds = matching_datasources[0]
    print(
        f"\nUsing published datasource '{selected_ds.name}' with ID: {selected_ds.id}"
    )
    return selected_ds.id


def list_workbooks_and_get_static_workbook_datasource_luid(
    server: TSC.Server, verbose: bool = False
) -> Optional[str]:
    """Find the SAMPLE_WORKBOOK sample workbook and return the LUID of its
    SAMPLE_STATIC_WORKBOOK_DATASOURCE static workbook datasource.

    Returns None (and prints a skip warning) when the sample workbook is
    not on the server or when the workbook has no static workbook
    datasource matching SAMPLE_STATIC_WORKBOOK_DATASOURCE.

    "Static workbook datasource" here refers to a datasource that lives
    inside a workbook and is addressed by ``datasourceLuid`` - distinct
    from the live-workbook flow, which addresses a datasource by
    ``workbookDatasourceId`` plus session headers.
    """
    if not server.auth_token:
        raise RuntimeError("Not signed in. Please call sign_in() first.")

    all_workbooks, pagination_item = server.workbooks.get()

    if verbose:
        print(f"\nThere are {pagination_item.total_available} workbooks on site:")
        for wb in all_workbooks:
            print(f"- {wb.name} (LUID: {wb.id})")

    matching_workbooks = [wb for wb in all_workbooks if wb.name == SAMPLE_WORKBOOK]
    if not matching_workbooks:
        print(
            f"\nSample workbook '{SAMPLE_WORKBOOK}' not found, "
            f"skipping static workbook datasource examples."
        )
        return None

    workbook = matching_workbooks[0]
    server.workbooks.populate_connections(workbook)

    if verbose:
        print(f"\nConnections for workbook '{workbook.name}':")
        for conn in workbook.connections:
            print(
                f"- datasource_name={conn.datasource_name!r} "
                f"datasource_id={conn.datasource_id!r}"
            )

    matching_connections = [
        conn
        for conn in workbook.connections
        if conn.datasource_name == SAMPLE_STATIC_WORKBOOK_DATASOURCE
        and conn.datasource_id
    ]
    if not matching_connections:
        print(
            f"\nStatic workbook datasource "
            f"'{SAMPLE_STATIC_WORKBOOK_DATASOURCE}' not found "
            f"in workbook '{SAMPLE_WORKBOOK}', "
            f"skipping static workbook datasource examples."
        )
        return None

    selected = matching_connections[0]
    print(
        f"\nUsing static workbook datasource '{selected.datasource_name}' "
        f"from workbook '{workbook.name}' with ID: {selected.datasource_id}"
    )
    return selected.datasource_id


def run_datasource_queries_sync(
    client: VizQLDataServiceClient,
    datasource: Datasource,
    args,
    label_suffix: str = "",
    skip_query_names: Optional[Iterable[str]] = None,
) -> None:
    """Run ReadMetadata, then each QUERY_FUNCTIONS query, then
    GetDatasourceModel against ``datasource`` using the sync client.

    ``label_suffix`` is appended to section headers and to the
    ``operation_name`` passed into handle_response / handle_error, so
    output from concurrent example runs (e.g. published datasource vs.
    static workbook datasource) remains distinguishable.

    ``skip_query_names`` names QUERY_FUNCTIONS entries (by ``__name__``)
    that should be skipped for this datasource - useful when the target
    datasource lacks fields that a query references.
    """
    skip = set(skip_query_names or ())
    try:
        print(f"\n=== ReadMetadata Query{label_suffix} ===")
        metadata_request = ReadMetadataRequest(datasource=datasource)
        if args.verbose:
            print(f"Request Body: {metadata_request}")

        metadata_response = read_metadata.sync_detailed(
            client=client, body=metadata_request
        )
        handle_response(
            metadata_response, f"ReadMetadata Query{label_suffix}", args.verbose
        )
    except Exception as e:
        handle_error(e, f"ReadMetadata Query{label_suffix}", args.verbose)

    for query_func in QUERY_FUNCTIONS:
        if query_func.__name__ in skip:
            print(
                f"\n=== ExecuteQuery: {query_func.__name__}{label_suffix} ==="
                f"\nSkipped (not applicable to this datasource)."
            )
            continue
        try:
            query_request = QueryRequest(query=query_func(), datasource=datasource)
            print(f"\n=== ExecuteQuery: {query_func.__name__}{label_suffix} ===")
            if args.verbose:
                print(f"Request Body: {query_request}")
            response = query_datasource.sync_detailed(client=client, body=query_request)
            handle_response(
                response, f"Query {query_func.__name__}{label_suffix}", args.verbose
            )
        except Exception as e:
            print(f"\n=== ExecuteQuery: {query_func.__name__}{label_suffix} ===")
            handle_error(e, f"Query {query_func.__name__}{label_suffix}", args.verbose)

    try:
        print(f"\n=== GetDatasourceModel{label_suffix} ===")
        datasource_model_request = GetDatasourceModelRequest(datasource=datasource)
        if args.verbose:
            print(f"Request Body: {datasource_model_request}")

        datasource_model_response = get_datasource_model.sync_detailed(
            client=client, body=datasource_model_request
        )
        handle_response(
            datasource_model_response,
            f"GetDatasourceModel{label_suffix}",
            args.verbose,
        )
    except Exception as e:
        handle_error(e, f"GetDatasourceModel{label_suffix}", args.verbose)


async def run_datasource_queries_async(
    client: VizQLDataServiceClient,
    datasource: Datasource,
    args,
    label_suffix: str = "",
    skip_query_names: Optional[Iterable[str]] = None,
) -> None:
    """Async twin of :func:`run_datasource_queries_sync`."""
    skip = set(skip_query_names or ())
    try:
        print(f"\n=== ReadMetadata Query{label_suffix} ===")
        metadata_request = ReadMetadataRequest(datasource=datasource)
        if args.verbose:
            print(f"Request Body: {metadata_request}")

        metadata_response = await read_metadata.asyncio_detailed(
            client=client, body=metadata_request
        )
        handle_response(
            metadata_response, f"ReadMetadata Query{label_suffix}", args.verbose
        )
    except Exception as e:
        handle_error(e, f"ReadMetadata Query{label_suffix}", args.verbose)

    for query_func in QUERY_FUNCTIONS:
        if query_func.__name__ in skip:
            print(
                f"\n=== ExecuteQuery: {query_func.__name__}{label_suffix} ==="
                f"\nSkipped (not applicable to this datasource)."
            )
            continue
        try:
            query_request = QueryRequest(query=query_func(), datasource=datasource)
            print(f"\n=== ExecuteQuery: {query_func.__name__}{label_suffix} ===")
            if args.verbose:
                print(f"Request Body: {query_request}")
            response = await query_datasource.asyncio_detailed(
                client=client, body=query_request
            )
            handle_response(
                response, f"Query {query_func.__name__}{label_suffix}", args.verbose
            )
        except Exception as e:
            print(f"\n=== ExecuteQuery: {query_func.__name__}{label_suffix} ===")
            handle_error(e, f"Query {query_func.__name__}{label_suffix}", args.verbose)

    try:
        print(f"\n=== GetDatasourceModel{label_suffix} ===")
        datasource_model_request = GetDatasourceModelRequest(datasource=datasource)
        if args.verbose:
            print(f"Request Body: {datasource_model_request}")

        datasource_model_response = await get_datasource_model.asyncio_detailed(
            client=client, body=datasource_model_request
        )
        handle_response(
            datasource_model_response,
            f"GetDatasourceModel{label_suffix}",
            args.verbose,
        )
    except Exception as e:
        handle_error(e, f"GetDatasourceModel{label_suffix}", args.verbose)


def create_datasource(luid: str) -> Datasource:
    """Create a Datasource object with the given LUID."""
    return Datasource(datasourceLuid=luid)


def create_workbook_datasource(workbook_datasource_id: str) -> Datasource:
    """Create a Datasource object referenced by workbookDatasourceId."""
    return Datasource(workbookDatasourceId=workbook_datasource_id)


def workbook_datasource_args_complete(args) -> bool:
    """Return True iff all three workbook-datasource-id CLI flags were
    supplied with non-empty values."""
    return bool(
        getattr(args, "workbook_datasource_id", None)
        and getattr(args, "global_session_header", None)
        and getattr(args, "x_session_id", None)
    )


def handle_response(response, query_name, verbose=False):
    """Handle the response from the API."""
    print(f"\n{query_name} Response:")

    if verbose:
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")

    print(f"Response Body: {response.content}")


def handle_error(e, operation_name: str = "Operation", verbose=False):
    """Handle exceptions and print detailed information.

    Args:
        e: The exception
        operation_name: Name of the operation for logging
        verbose: Whether to print detailed error information
    """
    print(f"\n{operation_name} failed: {str(e)}")
    if verbose:
        print_exception_details(e)


def print_exception_details(e):
    """Print detailed exception information"""
    print("\n=== Exception Details ===")
    print(f"Exception Type: {type(e).__name__}")
    print(f"Exception Message: {str(e)}")
    print("\n=== Full Traceback ===")
    traceback.print_exc()
    frame = inspect.currentframe()
    if frame:
        print("\n=== Current Frame Info ===")
        print(f"File: {frame.f_code.co_filename}")
        print(f"Line: {frame.f_lineno}")
        print(f"Function: {frame.f_code.co_name}")
        print("\nLocal Variables:")
        for name, value in frame.f_locals.items():
            print(f"  {name}: {type(value)} = {value}")


def create_server(
    url: str,
    *,
    username: Optional[str] = None,
    password: Optional[str] = None,
    pat_name: Optional[str] = None,
    pat_secret: Optional[str] = None,
    jwt_token: Optional[str] = None,
    site_id: str = "",
) -> tuple[str, Union[TSC.JWTAuth, TSC.PersonalAccessTokenAuth, TSC.TableauAuth]]:
    """Create a server configuration with authentication.

    Args:
        url: The base URL of the server.
        username: Username for Tableau authentication.
        password: Password for Tableau authentication.
        pat_name: Personal Access Token name (--pat-name).
        pat_secret: Personal Access Token secret (--pat-secret).
        jwt_token: JWT token for JWT authentication (--jwt-token).
        site_id: The site ID to use.

    Returns:
        tuple[str, Union[TSC.JWTAuth, TSC.PersonalAccessTokenAuth, TSC.TableauAuth]]:
            A tuple containing the formatted server URL and the authentication object.

    Raises:
        ValueError: If no valid authentication method is provided.
    """
    formatted_url = format_server_url(url)

    # Check for JWT authentication
    if jwt_token:
        auth: Union[TSC.JWTAuth, TSC.PersonalAccessTokenAuth, TSC.TableauAuth] = (
            TSC.JWTAuth(jwt_token, site_id=site_id)
        )
    # Check for Personal Access Token authentication
    elif pat_name and pat_secret:
        auth = TSC.PersonalAccessTokenAuth(pat_name, pat_secret, site_id=site_id)
    # Check for username/password authentication
    elif username and password:
        auth = TSC.TableauAuth(username, password, site_id=site_id)
    else:
        raise ValueError(
            "No valid authentication method provided. Please provide either:\n"
            "- JWT token (--jwt-token)\n"
            "- PAT name and secret (--pat-name, --pat-secret)\n"
            "- Username and password (--user, --password)"
        )

    return formatted_url, auth
