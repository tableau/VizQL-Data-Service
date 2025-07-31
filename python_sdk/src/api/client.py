import ssl
from importlib.metadata import version
from typing import Any, Optional, Union

import httpx
import tableauserverclient as TSC
from attrs import define, evolve, field

from .utils import format_server_url

API_SUBDOMAIN = "/api/v1/vizql-data-service"
X_TABLEAU_AUTH = "X-Tableau-Auth"
VERSION = version("vizql-data-service-py")  # Read version from package metadata


@define
class AuthenticatedClient:
    """A Client which has been authenticated for use on secured endpoints

    The following are accepted as keyword arguments and will be used to construct httpx Clients internally:

        ``base_url``: The base URL for the API, all requests are made to a relative path to this URL

        ``cookies``: A dictionary of cookies to be sent with every request

        ``headers``: A dictionary of headers to be sent with every request

        ``timeout``: The maximum amount of a time a request can take. API functions will raise
        httpx.TimeoutException if this is exceeded.

        ``verify_ssl``: Whether or not to verify the SSL certificate of the API server. This should be True in production,
        but can be set to False for testing purposes.

        ``follow_redirects``: Whether or not to follow redirects. Default value is False.

        ``httpx_args``: A dictionary of additional arguments to be passed to the ``httpx.Client`` and ``httpx.AsyncClient`` constructor.


    Attributes:
        raise_on_unexpected_status: Whether or not to raise an errors.UnexpectedStatus if the API returns a
            status code that was not documented in the source OpenAPI document. Can also be provided as a keyword
            argument to the constructor.
        token: The token to use for authentication
        prefix: The prefix to use for the Authorization header
        auth_header_name: The name of the Authorization header
    """

    raise_on_unexpected_status: bool = field(default=False, kw_only=True)
    _base_url: str = field(alias="base_url")
    _cookies: dict[str, str] = field(factory=dict, kw_only=True, alias="cookies")
    _headers: dict[str, str] = field(factory=dict, kw_only=True, alias="headers")
    _timeout: Optional[httpx.Timeout] = field(
        default=None, kw_only=True, alias="timeout"
    )
    _verify_ssl: Union[str, bool, ssl.SSLContext] = field(
        default=True, kw_only=True, alias="verify_ssl"
    )
    _follow_redirects: bool = field(
        default=False, kw_only=True, alias="follow_redirects"
    )
    _httpx_args: dict[str, Any] = field(factory=dict, kw_only=True, alias="httpx_args")
    _client: Optional[httpx.Client] = field(default=None, init=False)
    _async_client: Optional[httpx.AsyncClient] = field(default=None, init=False)

    token: str
    prefix: str = "Bearer"
    auth_header_name: str = "Authorization"

    def with_headers(self, headers: dict[str, str]) -> "AuthenticatedClient":
        """Get a new client matching this one with additional headers"""
        if self._client is not None:
            self._client.headers.update(headers)
        if self._async_client is not None:
            self._async_client.headers.update(headers)
        return evolve(self, headers={**self._headers, **headers})

    def with_cookies(self, cookies: dict[str, str]) -> "AuthenticatedClient":
        """Get a new client matching this one with additional cookies"""
        if self._client is not None:
            self._client.cookies.update(cookies)
        if self._async_client is not None:
            self._async_client.cookies.update(cookies)
        return evolve(self, cookies={**self._cookies, **cookies})

    def with_timeout(self, timeout: httpx.Timeout) -> "AuthenticatedClient":
        """Get a new client matching this one with a new timeout (in seconds)"""
        if self._client is not None:
            self._client.timeout = timeout
        if self._async_client is not None:
            self._async_client.timeout = timeout
        return evolve(self, timeout=timeout)

    def set_httpx_client(self, client: httpx.Client) -> "AuthenticatedClient":
        """Manually set the underlying httpx.Client

        **NOTE**: This will override any other settings on the client, including cookies, headers, and timeout.
        """
        self._client = client
        return self

    def _update_user_agent(self) -> None:
        """Update the User-Agent header to include the SDK identifier if not present."""
        sdk_prefix = "python-sdk/"
        sdk_identifier = f"{sdk_prefix}{VERSION}"
        if "User-Agent" not in self._headers:
            self._headers["User-Agent"] = sdk_identifier
        elif sdk_prefix not in self._headers["User-Agent"]:
            self._headers["User-Agent"] = (
                f"{self._headers['User-Agent']} {sdk_identifier}"
            )

    def get_httpx_client(self) -> httpx.Client:
        """Get the underlying httpx.Client, constructing a new one if not previously set"""
        if self._client is None:
            self._headers[self.auth_header_name] = (
                f"{self.prefix} {self.token}" if self.prefix else self.token
            )
            self._update_user_agent()
            self._client = httpx.Client(
                base_url=self._base_url,
                cookies=self._cookies,
                headers=self._headers,
                timeout=self._timeout,
                verify=self._verify_ssl,
                follow_redirects=self._follow_redirects,
                **self._httpx_args,
            )
        return self._client

    def __enter__(self) -> "AuthenticatedClient":
        """Enter a context manager for self.client—you cannot enter twice (see httpx docs)"""
        self.get_httpx_client().__enter__()
        return self

    def __exit__(self, *args: Any, **kwargs: Any) -> None:
        """Exit a context manager for internal httpx.Client (see httpx docs)"""
        self.get_httpx_client().__exit__(*args, **kwargs)

    def set_async_httpx_client(
        self, async_client: httpx.AsyncClient
    ) -> "AuthenticatedClient":
        """Manually the underlying httpx.AsyncClient

        **NOTE**: This will override any other settings on the client, including cookies, headers, and timeout.
        """
        self._async_client = async_client
        return self

    def get_async_httpx_client(self) -> httpx.AsyncClient:
        """Get the underlying httpx.AsyncClient, constructing a new one if not previously set"""
        if self._async_client is None:
            self._headers[self.auth_header_name] = (
                f"{self.prefix} {self.token}" if self.prefix else self.token
            )
            self._update_user_agent()
            self._async_client = httpx.AsyncClient(
                base_url=self._base_url,
                cookies=self._cookies,
                headers=self._headers,
                timeout=self._timeout,
                verify=self._verify_ssl,
                follow_redirects=self._follow_redirects,
                **self._httpx_args,
            )
        return self._async_client

    async def __aenter__(self) -> "AuthenticatedClient":
        """Enter a context manager for underlying httpx.AsyncClient—you cannot enter twice (see httpx docs)"""
        await self.get_async_httpx_client().__aenter__()
        return self

    async def __aexit__(self, *args: Any, **kwargs: Any) -> None:
        """Exit a context manager for underlying httpx.AsyncClient (see httpx docs)"""
        await self.get_async_httpx_client().__aexit__(*args, **kwargs)


class VizQLDataServiceClient:
    """Client for VizQL Data Service API."""

    def __init__(
        self,
        url: str,
        server: TSC.Server,
        auth: Union[TSC.JWTAuth, TSC.PersonalAccessTokenAuth, TSC.TableauAuth],
        verify_ssl: Union[str, bool, ssl.SSLContext] = True,
    ):
        """Initialize the client.

        Args:
            url: The base URL of the server.
            server: The Tableau Server instance.
            auth: The authentication object. Can be one of:
                - TSC.JWTAuth: JWT authentication (--jwt-token)
                - TSC.PersonalAccessTokenAuth: Personal access token authentication (--pat-name, --pat-secret)
                - TSC.TableauAuth: Tableau authentication (--user, --password)
            verify_ssl: Whether or not to verify the SSL certificate of the API server.
                This should be True in production, but can be set to False for testing purposes.
                Can also be a path to a CA bundle file or an ssl.SSLContext instance.
        """
        self.url = url
        self.server = server
        self.auth = auth
        self.verify_ssl = verify_ssl
        self._client = self._create_client()
        self.raise_on_unexpected_status = False

    def _create_client(self) -> AuthenticatedClient:
        """Create an authenticated client with proper server URL."""
        base_url = format_server_url(self.url, API_SUBDOMAIN)
        print(f"Server URL: {base_url}")

        return AuthenticatedClient(
            base_url=base_url,
            token=self.server.auth_token,
            prefix="",
            auth_header_name=X_TABLEAU_AUTH,
            verify_ssl=self.verify_ssl,
        )

    @property
    def client(self) -> AuthenticatedClient:
        """Get the authenticated client.

        Returns:
            AuthenticatedClient: The authenticated client instance.

        Raises:
            RuntimeError: If not signed in.
        """
        return self._client

    def get_httpx_client(self) -> httpx.Client:
        """Get the underlying httpx.Client."""
        return self.client.get_httpx_client()

    def get_async_httpx_client(self) -> httpx.AsyncClient:
        """Get the underlying httpx.AsyncClient."""
        return self.client.get_async_httpx_client()

    def __str__(self) -> str:
        return f"Client for {self.auth}"
