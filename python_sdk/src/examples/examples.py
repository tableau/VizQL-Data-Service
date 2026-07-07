import asyncio
import os
import sys

# Add project root to sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, root_dir)

# Determine if we're in development or production environment
is_development = os.path.basename(root_dir) == "python_sdk"

if is_development:
    import src.examples.async_examples as async_examples
    import src.examples.async_workbook_datasource_examples as async_workbook_datasource_examples
    import src.examples.common as common
    import src.examples.sync_examples as sync_examples
    import src.examples.sync_workbook_datasource_examples as sync_workbook_datasource_examples
else:
    import vizql_data_service_py.examples.async_examples as async_examples  # type: ignore
    import vizql_data_service_py.examples.async_workbook_datasource_examples as async_workbook_datasource_examples  # type: ignore  # noqa: E501
    import vizql_data_service_py.examples.common as common  # type: ignore
    import vizql_data_service_py.examples.sync_examples as sync_examples  # type: ignore
    import vizql_data_service_py.examples.sync_workbook_datasource_examples as sync_workbook_datasource_examples  # type: ignore  # noqa: E501

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
        asyncio.run(async_examples.execute(args))
        asyncio.run(async_workbook_datasource_examples.run(args))
    else:
        sync_examples.execute(args)
        sync_workbook_datasource_examples.run(args)
