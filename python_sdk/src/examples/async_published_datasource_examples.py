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
    from src.api.client import VizQLDataServiceClient
else:
    import vizql_data_service_py.examples.common as common  # type: ignore
    from vizql_data_service_py.api.client import VizQLDataServiceClient  # type: ignore


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
        client = VizQLDataServiceClient(
            server_url, server, auth, verify_ssl=not args.no_verify_ssl
        )
        datasource_luid = common.list_datasources_and_get_luid(server, args.verbose)
        datasource = common.create_datasource(datasource_luid)
        await common.run_datasource_queries_async(
            client, datasource, args, label_suffix=" (Published Datasource)"
        )
