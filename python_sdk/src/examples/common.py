import argparse
import inspect
import os
import sys
import traceback
from typing import Optional, Union

import tableauserverclient as TSC

# Add project root to sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, root_dir)

# Determine if we're in development or production environment
is_development = os.path.basename(root_dir) == "python_sdk"

if is_development:
    from src.api.openapi_generated import Datasource
    from src.api.utils import format_server_url
else:
    from vizql_data_service_py.api.openapi_generated import Datasource  # type: ignore
    from vizql_data_service_py.api.utils import format_server_url  # type: ignore

SAMPLE_DATASOURCE = "Superstore Datasource"


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
    print("  -h, --help                 Show this help message")

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
        "-h", "--help", action="store_true", help="Show this help message"
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
    print(f"\nUsing '{selected_ds.name}' with ID: {selected_ds.id}")
    return selected_ds.id


def create_datasource(luid: str) -> Datasource:
    """Create a Datasource object with the given LUID."""
    return Datasource(datasourceLuid=luid)


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
            TSC.JWTAuth(jwt_token, site_id)
        )
    # Check for Personal Access Token authentication
    elif pat_name and pat_secret:
        auth = TSC.PersonalAccessTokenAuth(pat_name, pat_secret, site_id)
    # Check for username/password authentication
    elif username and password:
        auth = TSC.TableauAuth(username, password, site_id)
    else:
        raise ValueError(
            "No valid authentication method provided. Please provide either:\n"
            "- JWT token (--jwt-token)\n"
            "- PAT name and secret (--pat-name, --pat-secret)\n"
            "- Username and password (--user, --password)"
        )

    return formatted_url, auth
