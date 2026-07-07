import os
import sys

import tableauserverclient as TSC

# Add project root to sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, root_dir)

# Determine if we're in development or production environment
is_development = os.path.basename(root_dir) == "python_sdk"

if is_development:
    import src.examples.common as common
    from src.api import query_datasource
    from src.api.client import VizQLDataServiceClient
    from src.api.openapi_generated import QueryRequest
    from src.examples.payload import WORKBOOK_QUERY_FUNCTIONS
else:
    import vizql_data_service_py.examples.common as common  # type: ignore
    from vizql_data_service_py.api import query_datasource  # type: ignore
    from vizql_data_service_py.api.client import VizQLDataServiceClient  # type: ignore
    from vizql_data_service_py.api.openapi_generated import (  # type: ignore
        QueryRequest,
    )
    from vizql_data_service_py.examples.payload import (  # type: ignore
        WORKBOOK_QUERY_FUNCTIONS,
    )


def run(args):
    if not common.workbook_datasource_args_complete(args):
        return
    server_url, auth = common.create_server(
        url=args.server,
        username=args.user,
        password=args.password,
        pat_name=args.pat_name,
        pat_secret=args.pat_secret,
        jwt_token=args.jwt_token,
        site_id=args.site,
    )
    server = TSC.Server(server_url)

    with server.auth.sign_in(auth):
        workbook_client = VizQLDataServiceClient(
            server_url,
            server,
            auth,
            global_session_header=args.global_session_header,
            x_session_id=args.x_session_id,
        )
        workbook_datasource = common.create_workbook_datasource(
            args.workbook_datasource_id
        )
        for query_func in WORKBOOK_QUERY_FUNCTIONS:
            try:
                query_request = QueryRequest(
                    query=query_func(), datasource=workbook_datasource
                )
                print(f"\n=== ExecuteWorkbookQuery: {query_func.__name__} ===")
                if args.verbose:
                    print(f"Request Body: {query_request}")
                response = query_datasource.sync_detailed(
                    client=workbook_client, body=query_request
                )
                common.handle_response(
                    response,
                    f"WorkbookQuery {query_func.__name__}",
                    args.verbose,
                )
            except Exception as e:
                print(f"\n=== ExecuteWorkbookQuery: {query_func.__name__} ===")
                common.handle_error(
                    e, f"WorkbookQuery {query_func.__name__}", args.verbose
                )
