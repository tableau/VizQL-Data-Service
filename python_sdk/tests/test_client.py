import ssl

import httpx
import tableauserverclient as TSC

from src.api.client import AuthenticatedClient, VizQLDataServiceClient


def test_authenticated_client_initialization():
    """Test basic initialization of AuthenticatedClient"""
    client = AuthenticatedClient(
        base_url="http://test.com",
        token="test-token",
        prefix="Bearer",
        auth_header_name="Authorization",
    )

    assert client.token == "test-token"
    assert client.prefix == "Bearer"
    assert client.auth_header_name == "Authorization"
    assert client._base_url == "http://test.com"


def test_authenticated_client_with_headers():
    """Test with_headers method"""
    client = AuthenticatedClient(base_url="http://test.com", token="test-token")

    new_client = client.with_headers({"X-Custom-Header": "test"})
    assert new_client._headers["X-Custom-Header"] == "test"
    assert new_client.token == client.token  # Ensure other attributes remain unchanged


def test_authenticated_client_with_cookies():
    """Test with_cookies method"""
    client = AuthenticatedClient(base_url="http://test.com", token="test-token")

    new_client = client.with_cookies({"session": "test-session"})
    assert new_client._cookies["session"] == "test-session"
    assert new_client.token == client.token  # Ensure other attributes remain unchanged


def test_authenticated_client_with_timeout():
    """Test with_timeout method"""
    client = AuthenticatedClient(base_url="http://test.com", token="test-token")

    timeout = httpx.Timeout(10.0)
    new_client = client.with_timeout(timeout)
    assert new_client._timeout == timeout
    assert new_client.token == client.token  # Ensure other attributes remain unchanged


def test_authenticated_client_get_httpx_client():
    """Test get_httpx_client method"""
    client = AuthenticatedClient(
        base_url="http://test.com",
        token="test-token",
        prefix="Bearer",
        auth_header_name="Authorization",
    )

    httpx_client = client.get_httpx_client()
    assert isinstance(httpx_client, httpx.Client)
    assert httpx_client.base_url == "http://test.com"
    assert httpx_client.headers["Authorization"] == "Bearer test-token"


def test_authenticated_client_context_manager():
    """Test context manager functionality"""
    client = AuthenticatedClient(base_url="http://test.com", token="test-token")

    with client as ctx_client:
        assert isinstance(ctx_client, AuthenticatedClient)
        assert ctx_client._client is not None


def test_vizql_data_service_client_initialization():
    """Test initialization of VizQLDataServiceClient"""
    server = TSC.Server("http://test.com")
    auth = TSC.TableauAuth("test-user", "test-password")
    server._auth_token = "test-auth-token"

    client = VizQLDataServiceClient(url="http://test.com", server=server, auth=auth)

    assert client.url == "http://test.com"
    assert client.server == server
    assert client.auth == auth
    assert isinstance(client._client, AuthenticatedClient)


def test_vizql_data_service_client_ssl_configuration():
    """Test SSL configuration options in VizQLDataServiceClient"""
    server = TSC.Server("http://test.com")
    auth = TSC.TableauAuth("test-user", "test-password")
    server._auth_token = "test-auth-token"

    # Test default SSL verification (True)
    client_default = VizQLDataServiceClient(
        url="http://test.com", server=server, auth=auth
    )
    assert client_default.verify_ssl is True
    assert client_default._client._verify_ssl is True

    # Test disabled SSL verification
    client_disabled = VizQLDataServiceClient(
        url="http://test.com", server=server, auth=auth, verify_ssl=False
    )
    assert client_disabled.verify_ssl is False
    assert client_disabled._client._verify_ssl is False

    # Test custom CA bundle path
    ca_bundle_path = "/path/to/ca-bundle.pem"
    client_ca_bundle = VizQLDataServiceClient(
        url="http://test.com", server=server, auth=auth, verify_ssl=ca_bundle_path
    )
    assert client_ca_bundle.verify_ssl == ca_bundle_path
    assert client_ca_bundle._client._verify_ssl == ca_bundle_path

    # Test custom SSL context
    ssl_context = ssl.create_default_context()
    client_ssl_context = VizQLDataServiceClient(
        url="http://test.com", server=server, auth=auth, verify_ssl=ssl_context
    )
    assert client_ssl_context.verify_ssl == ssl_context
    assert client_ssl_context._client._verify_ssl == ssl_context


def test_vizql_data_service_client_user_agent():
    """Test User-Agent handling in VizQLDataServiceClient"""
    server = TSC.Server("localhost")
    auth = TSC.TableauAuth("test-user", "test-password")
    server._auth_token = "test-auth-token"

    # Test case 1: No User-Agent
    client1 = VizQLDataServiceClient(url="localhost", server=server, auth=auth)
    httpx_client1 = client1.get_httpx_client()
    assert "python-sdk/" in httpx_client1.headers["User-Agent"]

    # Test case 2: Custom User-Agent
    client2 = VizQLDataServiceClient(url="localhost", server=server, auth=auth)
    client2.client._headers["User-Agent"] = "test-user-agent"
    httpx_client2 = client2.get_httpx_client()
    assert httpx_client2.headers["User-Agent"].startswith("test-user-agent")
    assert "python-sdk/" in httpx_client2.headers["User-Agent"]


def test_vizql_data_service_client_async_user_agent():
    """Test User-Agent handling in VizQLDataServiceClient async client"""
    server = TSC.Server("localhost")
    auth = TSC.TableauAuth("test-user", "test-password")
    server._auth_token = "test-auth-token"

    # Test case 1: No User-Agent
    client1 = VizQLDataServiceClient(url="localhost", server=server, auth=auth)
    async_client1 = client1.get_async_httpx_client()
    assert "python-sdk/" in async_client1.headers["User-Agent"]

    # Test case 2: Custom User-Agent
    client2 = VizQLDataServiceClient(url="localhost", server=server, auth=auth)
    client2.client._headers["User-Agent"] = "test-user-agent"
    async_client2 = client2.get_async_httpx_client()
    assert async_client2.headers["User-Agent"].startswith("test-user-agent")
    assert "python-sdk/" in async_client2.headers["User-Agent"]
