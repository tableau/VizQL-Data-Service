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
    from src.api import (
        get_datasource_model,
        query_datasource,
        read_metadata,
    )
    from src.api.client import VizQLDataServiceClient
    from src.api.openapi_generated import (
        GetDatasourceModelRequest,
        QueryRequest,
        ReadMetadataRequest,
    )
    from src.examples.payload import QUERY_FUNCTIONS
else:
    import vizql_data_service_py.examples.common as common  # type: ignore
    from vizql_data_service_py.api import (  # type: ignore
        get_datasource_model,
        query_datasource,
        read_metadata,
    )
    from vizql_data_service_py.api.client import VizQLDataServiceClient  # type: ignore
    from vizql_data_service_py.api.openapi_generated import (  # type: ignore
        GetDatasourceModelRequest,
        QueryRequest,
        ReadMetadataRequest,
    )
    from vizql_data_service_py.examples.payload import QUERY_FUNCTIONS  # type: ignore


async def execute(args):
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
        client = VizQLDataServiceClient(server_url, server, auth)
        datasource_luid = common.list_datasources_and_get_luid(server, args.verbose)
        datasource = common.create_datasource(datasource_luid)

        # Read metadata example
        try:
            print("\n=== ReadMetadata Query ===")
            metadata_request = ReadMetadataRequest(datasource=datasource)
            print(f"Request Body: {metadata_request}")

            metadata_response = await read_metadata.asyncio_detailed(
                client=client, body=metadata_request
            )
            common.handle_response(
                metadata_response, "ReadMetadata Query", args.verbose
            )
        except Exception as e:
            common.handle_error(e, "ReadMetadata Query", args.verbose)

        # Query data source examples
        async def execute_query(query_func):
            try:
                query_request = QueryRequest(query=query_func(), datasource=datasource)
                print(f"\n=== ExecuteQuery: {query_func.__name__} ===")
                if args.verbose:
                    print(f"Request Body: {query_request}")

                response = await query_datasource.asyncio_detailed(
                    client=client, body=query_request
                )
                common.handle_response(
                    response, f"Query {query_func.__name__}", args.verbose
                )
            except Exception as e:
                print(f"\n=== ExecuteQuery: {query_func.__name__} ===")
                common.handle_error(e, f"Query {query_func.__name__}", args.verbose)

        # Execute queries sequentially
        for query_func in QUERY_FUNCTIONS:
            await execute_query(query_func)

        # Get datasource model example
        try:
            print("\n=== GetDatasourceModel ===")
            datasource_model_request = GetDatasourceModelRequest(datasource=datasource)
            if args.verbose:
                print(f"Request Body: {datasource_model_request}")

            datasource_model_response = await get_datasource_model.asyncio_detailed(
                client=client, body=datasource_model_request
            )
            common.handle_response(
                datasource_model_response, "GetDatasourceModel", args.verbose
            )
        except Exception as e:
            common.handle_error(e, "GetDatasourceModel", args.verbose)
