import asyncio
import os
import sys

# Add project root to sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, root_dir)

# Determine if we're in development or production environment
is_development = os.path.basename(root_dir) == "python_sdk"

if is_development:
    import src.examples.async_live_workbook_examples as async_live_workbook_examples
    import src.examples.async_published_datasource_examples as async_published_datasource_examples
    import src.examples.common as common
    import src.examples.sync_live_workbook_examples as sync_live_workbook_examples
    import src.examples.sync_published_datasource_examples as sync_published_datasource_examples
else:
    import vizql_data_service_py.examples.async_live_workbook_examples as async_live_workbook_examples  # type: ignore
    import vizql_data_service_py.examples.async_published_datasource_examples as async_published_datasource_examples  # type: ignore
    import vizql_data_service_py.examples.common as common  # type: ignore
    import vizql_data_service_py.examples.sync_live_workbook_examples as sync_live_workbook_examples  # type: ignore
    import vizql_data_service_py.examples.sync_published_datasource_examples as sync_published_datasource_examples  # type: ignore

if __name__ == "__main__":
    # Check for help flag before parsing arguments
    if "-h" in sys.argv or "--help" in sys.argv:
        common.print_help()
        sys.exit(0)

    parser = common.parse_arguments()
    parser.add_argument(
        "--async",
        dest="async_mode",
        action="store_true",
        help="Run examples in async mode",
    )
    args = parser.parse_args()

    if args.async_mode:
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(async_published_datasource_examples.execute(args))
        asyncio.run(async_live_workbook_examples.run(args))
    else:
        sync_published_datasource_examples.execute(args)
        sync_live_workbook_examples.run(args)
