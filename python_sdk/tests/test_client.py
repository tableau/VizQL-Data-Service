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


def test_vizql_data_service_client_with_headers_returns_clone():
    """with_headers returns a new VizQLDataServiceClient that sends extra
    headers on every request, without mutating the original client."""
    server = TSC.Server("http://test.com")
    auth = TSC.TableauAuth("test-user", "test-password")
    server._auth_token = "test-auth-token"

    client = VizQLDataServiceClient(url="http://test.com", server=server, auth=auth)

    # Realize the original httpx.Client so we can check it is left untouched.
    original_httpx = client.get_httpx_client()
    assert "Global-Session-Header" not in original_httpx.headers

    new_client = client.with_headers(
        {"Global-Session-Header": "gsh", "X-Session-Id": "sid"}
    )
    assert isinstance(new_client, VizQLDataServiceClient)
    assert new_client is not client
    assert new_client.url == client.url
    assert new_client.server is client.server
    assert new_client.auth is client.auth
    assert new_client.verify_ssl == client.verify_ssl

    new_httpx = new_client.get_httpx_client()
    assert new_httpx.headers["Global-Session-Header"] == "gsh"
    assert new_httpx.headers["X-Session-Id"] == "sid"
    # Authentication headers carry over to the new client.
    assert new_httpx.headers["X-Tableau-Auth"] == "test-auth-token"

    # The original client must NOT have picked up the extra headers.
    assert "Global-Session-Header" not in original_httpx.headers
    assert "X-Session-Id" not in original_httpx.headers


def test_vizql_data_service_client_with_headers_async_carries_headers():
    """The cloned client's async httpx client must also carry the extra
    headers — the sync and async sides are independent lazy clients."""
    server = TSC.Server("http://test.com")
    auth = TSC.TableauAuth("test-user", "test-password")
    server._auth_token = "test-auth-token"

    client = VizQLDataServiceClient(url="http://test.com", server=server, auth=auth)
    # Realize the original async client to confirm it is left untouched.
    original_async = client.get_async_httpx_client()
    assert "Global-Session-Header" not in original_async.headers

    new_client = client.with_headers(
        {"Global-Session-Header": "gsh", "X-Session-Id": "sid"}
    )
    new_async = new_client.get_async_httpx_client()
    assert new_async.headers["Global-Session-Header"] == "gsh"
    assert new_async.headers["X-Session-Id"] == "sid"
    assert new_async.headers["X-Tableau-Auth"] == "test-auth-token"

    assert "Global-Session-Header" not in original_async.headers
    assert "X-Session-Id" not in original_async.headers


def test_vizql_data_service_client_with_headers_preserves_inner_fields():
    """with_headers must preserve all AuthenticatedClient fields that aren't
    being overridden (cookies, timeout, follow_redirects, httpx_args,
    raise_on_unexpected_status, prefix, auth_header_name)."""
    server = TSC.Server("http://test.com")
    auth = TSC.TableauAuth("test-user", "test-password")
    server._auth_token = "test-auth-token"

    client = VizQLDataServiceClient(url="http://test.com", server=server, auth=auth)
    # Pre-configure non-header fields on the inner client.
    client._client = client._client.with_cookies({"session": "orig-session"})
    client._client = client._client.with_timeout(httpx.Timeout(7.5))
    client._client._headers["X-Preexisting"] = "kept"
    client._client.raise_on_unexpected_status = True

    new_client = client.with_headers({"Global-Session-Header": "gsh"})
    inner = new_client.client
    # Header merge: caller's header is added, pre-existing header is preserved.
    assert inner._headers.get("Global-Session-Header") == "gsh"
    assert inner._headers.get("X-Preexisting") == "kept"
    # Non-header fields survive evolve.
    assert inner._cookies == {"session": "orig-session"}
    assert inner._timeout == httpx.Timeout(7.5)
    assert inner.raise_on_unexpected_status is True


def test_vizql_data_service_client_with_headers_does_not_mutate_inner_headers():
    """Mutating the headers dict passed to with_headers — or the original
    inner client — after the call must not change what the clone sends."""
    server = TSC.Server("http://test.com")
    auth = TSC.TableauAuth("test-user", "test-password")
    server._auth_token = "test-auth-token"

    client = VizQLDataServiceClient(url="http://test.com", server=server, auth=auth)
    headers_arg = {"Global-Session-Header": "gsh"}
    new_client = client.with_headers(headers_arg)
    # Mutate the caller's dict; the clone must be unaffected.
    headers_arg["Global-Session-Header"] = "tampered"
    assert new_client.client._headers["Global-Session-Header"] == "gsh"


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
