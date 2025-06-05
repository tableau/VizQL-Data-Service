# VizQL Data Service Python SDK 

[![Tableau Supported](https://img.shields.io/badge/Support%20Level-Tableau%20Supported-53bd92.svg)](https://www.tableau.com/support-levels-it-and-developer-tools)
[![GitHub](https://img.shields.io/badge/license-Apache%202.0-blue?style=flat-square.svg)](https://raw.githubusercontent.com/tableau/VizQL-Data-Service/refs/heads/main/python_sdk/LICENSE.txt)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
<!-- Enable after publish in production
[![PyPI Version](https://img.shields.io/pypi/v/vizql-data-service-py.svg)](https://pypi.org/project/vizql-data-service-py/)
[![Downloads](https://img.shields.io/pypi/dm/vizql-data-service-py.svg)](https://pypi.org/project/vizql-data-service-py/)
[![Build](https://github.com/tableau/VizQL-Data-Service/actions/workflows/push.yml/badge.svg)](https://github.com/tableau/VizQL-Data-Service/actions/workflows/push.yml)
Add code coverage
-->
[![OpenAPI](https://img.shields.io/badge/OpenAPI-3.0.3-green.svg)](https://raw.githubusercontent.com/tableau/VizQL-Data-Service/refs/heads/main/VizQLDataServiceOpenAPISchema.json)

The VizQL Data Service Python SDK is a lightweight client library that enables interaction with Tableau's VizQL Data Service APIs. It supports both cloud and on-premises deployments, offering both synchronous and asynchronous methods for querying the VizQL Data Service APIs.

Consider reading VizQL Data Service in the following order:
- [VizQL Data Service help documentation](https://help.tableau.com/current/api/vizql-data-service/en-us/index.html)
- [VizQL Data Service API Reference](https://help.tableau.com/current/api/vizql-data-service/en-us/reference/index.html)
- [VizQL Data Service Postman collection](https://www.postman.com/salesforce-developers/salesforce-developers/folder/jdy4gr3/vizql-data-service-queries)
- [VizQL Data Service OpenAPI Schema](https://github.com/tableau/VizQL-Data-Service/blob/main/VizQLDataServiceOpenAPISchema.json)

## Version Support
The VizQL Data Service Python SDK supports different versions of the VizQLDataServiceOpenAPISchema. Past versions of the schema corresponding to past releases of Tableau can be found in the release branches with name `release-[year].[quarter]`. As an example, `release-20251.0` contains the VizQLDataServiceOpenAPISchema corresponding to 20251.0 (as a special note, the 20251.0 release uniquely does not have Python SDK support). `release-20252.0` contains the schema corresponding to 20252.0 and the Python SDK that supports 20252.0. The main branch will always contain the most recent version of the VizQLDataServiceOpenAPISchema as well as the Python SDK that supports it.

### Schema Versions
[20251.0](https://github.com/tableau/VizQL-Data-Service/blob/release-20251.0/VizQLDataServiceOpenAPISchema.json)

[20252.0](https://github.com/tableau/VizQL-Data-Service/blob/main/VizQLDataServiceOpenAPISchema.json)

### Python SDK Versions
None for 20251.0

[20252.0](https://github.com/tableau/VizQL-Data-Service/tree/main/python_sdk)

## 🔧 Installation
```bash
python -m venv --system-site-packages venv # Optional command: set up a python virtual environment before installing the vizql_data_service_py package
source venv/bin/activate    # A continuation of the first command for Unix/MacOS users. This activates the virtual environment for Unix/MacOS
venv\Scripts\activate       # A continuation of the first command for Windows users. This activates the virtual environment for Windows

pip install vizql-data-service-py
```

## 🚀 Quick Start

### Importing Required Modules
```python
from vizql_data_service_py import (
    ReadMetadataRequest,
    QueryRequest,
    Datasource,
    Connection,
    VizQLDataServiceClient,
    read_metadata,
    query_datasource,
    DimensionField,
    MeasureField,
    Function,
    Query
)
```

### Setting Up Server Connection
To create Server and Auth instances, please refer to the [Tableau Server Client (Python) Authentication Guide](https://tableau.github.io/server-client-python/docs/sign-in-out). For JWT authentication setup, see the [Configure Connected Apps with Direct Trust](https://help.tableau.com/current/online/en-us/connected_apps_direct.htm) documentation.

> **Note**: Authentication methods vary between Tableau Cloud and On-premises deployments:
> - Tableau Cloud: Supports JWT and Personal Access Token (PAT) authentication
> - Tableau On-premises: Supports JWT, PAT, and username/password authentication

### Configuring Data Source
```python
# Create a data source instance with optional connection parameters
datasource = Datasource(
    datasourceLuid="<datasource-luid>",
    # Optional: Configure connections for external data sources
    connections=[
        Connection(
            connectionUsername="<connection-username>",
            connectionPassword="<connection-password>"
        )
    ]
)
```

### Sign in, Read Metadata and Query Data Sources
```python
import tableauserverclient as TSC

# Choose one of these auth mechanisms
tableau_auth = TSC.PersonalAccessTokenAuth('TOKEN_NAME', 'TOKEN_VALUE', 'SITENAME')
# tableau_auth = TSC.TableauAuth('USERNAME', 'PASSWORD', 'SITENAME')
# tableau_auth = TSC.JWTAuth('JWT', 'SITENAME')

server_url = 'https://SERVER_URL'
server = TSC.Server(server_url)

with server.auth.sign_in(tableau_auth):
    client = VizQLDataServiceClient(server_url, server, tableau_auth)
    # Define your query fields
    query = Query(
        # Example: sample Superstore data source
        # Aggregate SUM(Sales) by Category
        fields=[
            DimensionField(fieldCaption="Category"),
            MeasureField(fieldCaption="Sales", function=Function.SUM),
        ]
    )
    # Step 1: Read metadata
    read_metadata_request = ReadMetadataRequest(
        datasource=datasource
    )
    read_metadata_response = read_metadata.sync(
        client=client, body=read_metadata_request
    )
    print(f"Read Metadata Response: {read_metadata_response}")

    # Step 2: Execute query
    query_request = QueryRequest(
        query=query, datasource=datasource
    )
    query_response = query_datasource.sync(
        client=client, body=query_request
    )
    print(f"Query Datasource Response: {query_response}")
```

### API Methods
The SDK provides two ways to make API calls:

```python
# Simple way - just get the response data
response = read_metadata.sync(client=client, body=read_metadata_request)

# Detailed way - get response data, status code and headers
response, status, headers = read_metadata.sync_detailed(client=client, body=read_metadata_request)
```

Both methods work for `read_metadata` and `query_datasource`. Use `sync_detailed()` when you need HTTP response details like status code and headers.

This SDK is built using `datamodel-codegen` to generate all VizQL Data Service models based on Pydantic v2. For detailed API documentation and model specifications, please refer to the [VizQLDataServiceOpenAPISchema.json](https://github.com/tableau/VizQL-Data-Service/blob/main/VizQLDataServiceOpenAPISchema.json) file. 

> **Note**: While raw JSON requests are supported, we strongly recommend using the provided Python pydantic v2 objects to construct requests. This approach offers several advantages:
> - Type safety and validation at compile time
> - Better IDE support with autocompletion
> - Consistent request structure
> - Easier maintenance and debugging

For comprehensive examples demonstrating various query patterns and filter combinations, please check the [examples](https://github.com/tableau/VizQL-Data-Service/tree/main/python_sdk/src/examples) directory.

## 📘 Supported Features
- ✅ Read metadata of Tableau published datasources
- ✅ Query published datasources with selectable fields and queries supports various filters
- ✅ Synchronous and Asynchronous Python client support
- ✅ Authentication using Tableau username/password, JWT or PAT
- ✅ Works with both Tableau Cloud and Tableau Server (on-prem)
- ✅ OpenAPI schema generated Python Pydantic v2 models for type-safe API interactions

## 🛠️ Requirements
- Python 3.9+
- pip 20.0+
- Tableau Server 2025.1+ or Tableau Cloud

## 🤝 Contributing
To contribute, see our [CONTRIBUTING.md](https://github.com/tableau/VizQL-Data-Service/blob/main/python_sdk/CONTRIBUTING.md) Guide. A list of all our contributors to date is in [CONTRIBUTORS.md](https://github.com/tableau/VizQL-Data-Service/blob/main/python_sdk/CONTRIBUTORS.md).
