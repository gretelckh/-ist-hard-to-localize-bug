# Fault-nature classification of the 293 not-reproduced bugs

> Inferred from each issue's body/title (no runtime evidence exists). Only determinable natures are assigned; ambiguous bugs are left as `unknown`. This is a fault-NATURE taxonomy, NOT the exposure channel and NOT the Taraghi taxonomy (deliberately unused).

## Distribution (n=293)

| Fault nature | # | % of 293 |
|---|---:|---:|
| transport/connection | 159 | 54.3% |
| auth/credentials | 33 | 11.3% |
| lifecycle/concurrency | 21 | 7.2% |
| protocol/spec | 19 | 6.5% |
| serialisation/parsing | 18 | 6.1% |
| discovery/routing | 14 | 4.8% |
| environment/packaging | 10 | 3.4% |
| example/demo | 6 | 2.0% |
| external-dependency | 6 | 2.0% |
| error handling/reporting | 5 | 1.7% |
| unknown | 2 | 0.7% |

> `unknown` = 2 bugs whose body/title did not match any nature category; left blank rather than guessed.

## Per-bug table

| Issue | Origin | Fault nature | Title |
|---|---|---|---|
| 79 | Client | lifecycle/concurrency | `RuntimeError: Attempted to exit cancel scope in a different task than |
| 88 | Client | lifecycle/concurrency | Random error thrown on response |
| 280 | Client | serialisation/parsing | AttributeError: 'JSONRPCMessage' object has no attribute 'message' in  |
| 332 | Client | transport/connection | Client requests hang forever if server dies |
| 341 | Client | error handling/reporting | Wrong types for logging_callback in Client. The callback is never call |
| 359 | Client | transport/connection | stdio_client not starting in windows: getting NotImplementedError |
| 360 | Client | transport/connection | stdio_client context manager hangs |
| 369 | Client | lifecycle/concurrency | NotImplementedError in asyncio subprocess_exec when using MCP client o |
| 382 | Client | transport/connection | `stdio_client` hangs during `session.initialize()` due to failed messa |
| 409 | Client | auth/credentials | Error from MCP server: SyntaxError: Unexpected token 'E', "Error: typ" |
| 410 | Client | transport/connection | The Python MCP server hangs when the `/messages` endpoint gives an une |
| 483 | Client | transport/connection | AssertionError in ClientSession.initialize() when writing to anyio std |
| 521 | Client | lifecycle/concurrency | RuntimeError: Attempted to exit cancel scope in a different task than  |
| 542 | Client | transport/connection | MCP server with STDIO transport throws an 'Error: SSE connection not e |
| 543 | Client | transport/connection | [BUG] session.initialize() hangs indefinitely with stdio_client setup |
| 552 | Client | transport/connection | On Windows 11 when you initialize an mcp client it hangs indefinitely |
| 572 | Client | transport/connection | `NotImplementedError` on Windows with `stdio_client` and default `asyn |
| 575 | Client | lifecycle/concurrency | Bug: RuntimeError during cleanup on Windows – no running event loop |
| 577 | Client | lifecycle/concurrency | `RuntimeError: Attempted to exit cancel scope in a different task` whe |
| 583 | Client | transport/connection | SSE connection not established while trying to list tools via inspecto |
| 616 | Client | auth/credentials | When no authorization is required dont fail on missing user scope 401  |
| 623 | Client | transport/connection | MCP Inspector can't connect with mcp server |
| 668 | Client | protocol/spec | Will not work if multiple MCP inspector windows are open |
| 691 | Client | serialisation/parsing | 'JSONRPCMessage' object has no attribute 'message' in mcp 1.8.0 |
| 716 | Client | transport/connection | ValueError: I/O operation on closed pipe |
| 737 | Client | transport/connection | Bug Report: FastMCP `RuntimeError: Received request before initializat |
| 788 | Client | transport/connection | adding multiple servers using the ClientSessionGroup, an error occurs  |
| 814 | Client | auth/credentials | OAuthMetadata as define is too restrivtive, hence produces a Validatio |
| 817 | Client | transport/connection | STDIO hangs forever when the  using multiprocessing in tools |
| 831 | Client | transport/connection | Errors during cleanup when using streamablehttp_client with AsyncExitS |
| 874 | Client | transport/connection | Cannot break out of session.initialize() when using streamable-http |
| 892 | Client | serialisation/parsing | Validation error when listing resources in simple-resource server exam |
| 906 | Client | transport/connection | Error in post_writer: Server disconnected without sending a response. |
| 915 | Client | transport/connection | Exception in `ClientSessionGroup` if `streamable_http` MCP server is n |
| 922 | Client | lifecycle/concurrency | Create and Close multiple client session result "RuntimeError: Attempt |
| 1097 | Client | transport/connection | Roots/List Request Hangs in Client-Server Communication |
| 1100 | Client | transport/connection | MCP connection fails silently |
| 1141 | Client | transport/connection | Progress notifications cause server to hang on stdio transport |
| 1152 | Client | lifecycle/concurrency | CancelledError causes duplicate response and server crash |
| 1173 | Client | auth/credentials | Response parsing errors after OAuth flow |
| 1192 | Client | protocol/spec | Auth server metadata fallbacks abort on non-404 failures |
| 1212 | Client | error handling/reporting | When throwing the HTTP status exception, MCP client is disregarding th |
| 1214 | Client | lifecycle/concurrency | Unhandled GeneratorExit error |
| 1227 | Client | transport/connection | SSE: ConnectionClosed exception after session disconnect |
| 1307 | Client | auth/credentials | Error & Mismatch in OAuth scope resolution between Claude.ai/MCP Pytho |
| 1313 | Client | auth/credentials | SyntaxError: Unexpected token '?' |
| 1318 | Client | auth/credentials | Critical Token Refresh Bugs - Prevents Proactive Refresh |
| 1379 | Client | auth/credentials | Visual Studio Code cannot authorize with FastMCP OAuth |
| 1382 | Client | transport/connection | Cannot handle `Unexpected content type` when initializing MCP session |
| 1400 | Client | discovery/routing | RFC 9728 compliance: protected resource metadata URL mismatches when r |
| 1415 | Client | lifecycle/concurrency | MCP Python SDK Protocol Compliance Gap: Missing Direction Validation f |
| 1416 | Client | protocol/spec | buggg |
| 1420 | Client | lifecycle/concurrency | MCP Python SDK Protocol Compliance Gap-2: Missing Logging and Propagat |
| 1421 | Client | protocol/spec | MCP Python SDK Implementation Gap-3: Missing Built-in Rate Limiting fo |
| 1422 | Client | protocol/spec | MCP Python SDK Implementation Gap-4: Missing Configurable Ping Frequen |
| 1423 | Client | transport/connection | MCP Python SDK Implementation Gap-5: Missing Automatic Ping Mechanism  |
| 1442 | Client | auth/credentials | MCP Python SDK Implementation Gap-10: MCP Python SDK Client Missing To |
| 1443 | Client | auth/credentials | MCP Python SDK Implementation Gap-11: Server Missing Resource Validati |
| 1444 | Client | auth/credentials | MCP Python SDK Implementation Gap-12: Server Missing Token Validation  |
| 1445 | Client | auth/credentials | MCP Python SDK Implementation Gap-13: Server Missing Token Issuer Vali |
| 1452 | Client | transport/connection | The `stdio_client` hangs indefinitely on session initialization |
| 1458 | Client | transport/connection | MCP Python SDK Implementation Gap-17: Missing Cancellation Notificatio |
| 1470 | Client | protocol/spec | SSLV3_ALERT_HANDSHAKE_FAILURE when using private gateway |
| 1480 | Client | auth/credentials | Token endpoint returns incorrect error code for client authentication  |
| 1495 | Client | discovery/routing | Protected Resource Metadata request failed: 404 |
| 1513 | Client | transport/connection | MCP SDK Pydantic v2 Compatibility Bug Report |
| 1564 | Client | transport/connection | stdio_client fails with BrokenResourceError during initialization |
| 1600 | Client | auth/credentials | progressToken type mismatch breaks progress callback between spring-ai |
| 1602 | Client | auth/credentials | OAuth: 403 responses without insufficient_scope incorrectly retry with |
| 1648 | Client | transport/connection | ClientDisconnect returns HTTP 500 |
| 1658 | Client | serialisation/parsing | ClosedResourceError when using FastMCP(..., stateless_http=True, json_ |
| 1672 | Client | transport/connection | Python MCP Client ValidationError: Empty SSE data causes JSON parsing  |
| 1716 | Client | lifecycle/concurrency | Getting RuntimeError: Task group is not initialized. Make sure to use  |
| 1717 | Client | transport/connection | UnboundLocalError in send_request when response_or_error is not assign |
| 1742 | Client | transport/connection | Introduce typed error classes with metadata |
| 1744 | Client | lifecycle/concurrency | Improve exception tracebacks for easier debugging |
| 1789 | Client | transport/connection | Client hangs forever |
| 1796 | Client | serialisation/parsing | Pydantic ValidationError when a call_tool response contains structured |
| 1805 | Client | transport/connection | Possible ressource leak / race condition in streamable_http_client |
| 1821 | Client | serialisation/parsing | Clarify JSON-RPC error code for 'session not found' responses |
| 1830 | Client | transport/connection | CancelledError from connection failures is indistinguishable from exte |
| 1844 | Client | transport/connection | SSE transport: "Received request before initialization was complete" e |
| 1933 | Client | transport/connection | Using transport="stdio" closes real stdio, causing ValueError after se |
| 1960 | Client | transport/connection | BrokenResourceError race condition in stdio_client cleanup when contex |
| 2064 | Client | transport/connection | ClientDisconnect during _handle_post_request crashes stateless session |
| 2107 | Client | transport/connection | Handle list_changed notifications instead of dropping them |
| 2128 | Client | auth/credentials | ClientCredentialsOAuthProvider: Missing client_id in token request bod |
| 2205 | Client | auth/credentials | Incorrect `ProtectedResourceMetadata` model for oauth authentication |
| 2216 | Client | protocol/spec | Bug: validate_scope rejects client scopes when required scopes in None |
| 2260 | Client | auth/credentials | Server OAuth metadata hardcodes token_endpoint_auth_methods_supported, |
| 2416 | Client | transport/connection | Bug: AssertionError: Request already responded to — cancellation race  |
| 2480 | Client | lifecycle/concurrency | RequestResponder.cancel sends JSON-RPC response, violating cancellatio |
| 2548 | Client | protocol/spec | BaseSession.send_request fails when forwarding a request received via  |
| 2564 | Client | error handling/reporting | raise without from discards exception chain in 12 remaining sites |
| 2577 | Client | auth/credentials | MCP client does not retry authenticated request after successful OAuth |
| 2605 | Client | transport/connection | Duplicate `initialize` with changed parameters can overwrite `ServerSe |
| 2610 | Client | transport/connection | RequestResponder.__exit__ leaks CancelledError on cancelled request, k |
| 2641 | Client | auth/credentials | Add `invalid_target` to `AuthorizationErrorCode` (RFC 8707) |
| 2644 | Client | auth/credentials | Bug: `anyio.Lock` in `oauth2.py` raises "current task is not holding t |
| 2673 | Client | lifecycle/concurrency | ClientSession receive loop swallows callback exceptions, replying "Inv |
| 2687 | Client | auth/credentials | `OAuthClientInformationFull.redirect_uris`: pydantic strict-type-equal |
| 2847 | Client | auth/credentials | Bug: anyio.Lock in async_auth_flow causes RuntimeError under concurren |
| 2883 | Client | discovery/routing | AnyHttpUrl normalization adds trailing slash → breaks RFC 9728 canonic |
| 3103 | Client | auth/credentials | RequireAuthMiddleware omits RFC 6750 scope in WWW-Authenticate on 401/ |
| 3174 | Client | serialisation/parsing | [v2] JSON-RPC error responses leave client OpenTelemetry spans UNSET |
| 3209 | Client | auth/credentials | Bug: OAuth provider holds context.lock for the whole request, so the s |
| 3240 | Client | auth/credentials | OAuth token refresh hits the wrong endpoint when the auth server lives |
| 3250 | Client | auth/credentials | OAuthClientProvider._initialize() breaks transparent refresh: missing  |
| 3273 | Client | transport/connection | [v2] ping returns 'Method not found' on 2026-07-28 connections: ping m |
| 3382 | Client | auth/credentials | OAuthClientProvider auth lock is permanently poisoned when httpx close |
| 3384 | Client | discovery/routing | ClientSessionGroup raises KeyError when a server exposes no tools, res |
| 3483 | Client | protocol/spec | Client never retries after -32020 HeaderMismatch, and there is no publ |
| 3490 | Client | transport/connection | ClientSessionGroup: a rejected connect_to_server leaves its transport  |
| 3566 | Client | auth/credentials | OAuth client scope handling breaks on comma-separated scope strings |
| 78 | Host | example/demo | Example server and client not working |
| 111 | Host | external-dependency | Requirement name `mcp` matches project name `mcp` |
| 122 | Host | serialisation/parsing | Maybe: using standand openai base url is not working |
| 124 | Host | environment/packaging | pip install mcp - Unable to find FastMCP |
| 127 | Host | transport/connection | Fail to import FastMCP |
| 131 | Host | environment/packaging | npx / node not found using lazy node with zsh |
| 146 | Host | environment/packaging | error: No `pyproject.toml` found in current directory or any parent di |
| 147 | Host | transport/connection | MCP server disconnected |
| 148 | Host | environment/packaging | bug: mcp server installation doesn't work |
| 163 | Host | example/demo | Demo MCP and others are now failing for |
| 164 | Host | external-dependency | Claude Desktop breaking down after asking to execute tool |
| 182 | Host | transport/connection | Failed to run server: Server.run() missing 3 required positional argum |
| 184 | Host | auth/credentials | inspector Unexpected token { |
| 201 | Host | transport/connection | Client hangs when ctx.info() logging with pure Python client |
| 240 | Host | environment/packaging | Cannot start client with npx |
| 252 | Host | lifecycle/concurrency | Error during cleanup of server sqlite: Attempted to exit cancel scope  |
| 298 | Host | unknown | Python tool call longer than 3-5sec freezes and breaks the code |
| 326 | Host | transport/connection | MCP client with npx not working when env parameter of StdioServerParam |
| 334 | Host | environment/packaging | MCP Server Initialization Fails with "spawn uv ENOENT" Error |
| 478 | Host | protocol/spec | Fix ENOENT error when installing MCP server with `mcp install server.p |
| 533 | Host | transport/connection | Example servers, ImportError during running |
| 663 | Host | transport/connection | When I connect to Python Server using Java Client, I get a 'Received r |
| 679 | Host | protocol/spec | Running Simple Auth Github Example throws 404 error |
| 768 | Host | transport/connection | Client example 'mcp_simple_auth' cannot connect to the server |
| 780 | Host | discovery/routing | mcp dev server.py Error: Cannot find module '../lib/cli.js' |
| 804 | Host | environment/packaging | 'uv run mcp' command does not work ! It gives me this [see screenshot] |
| 813 | Host | transport/connection | MCP SDK hangs |
| 852 | Host | transport/connection | Client Registration Fails with 502 Error When Connecting to Auth Serve |
| 854 | Host | transport/connection | stdio_client Fails with AttributeError: 'StreamToLogger' object has no |
| 862 | Host | transport/connection | mcp.client.stdio Hangs |
| 888 | Host | transport/connection | import error |
| 1082 | Host | serialisation/parsing | A JavaScript error occurred in the main process |
| 1103 | Host | transport/connection | MCP client not able to initiate StdioServerParameters while running in |
| 1210 | Host | external-dependency | Simple Auth example doesn't work with Claude Desktop |
| 1213 | Host | lifecycle/concurrency | AsyncExitStack fails to close at the first attempt |
| 1350 | Host | external-dependency | Issue: Sticky Session / Session Affinity Not Working with Azure Web Ap |
| 1451 | Host | serialisation/parsing | Build failure on Python 3.14 due to outdated pydantic-core dependency |
| 1469 | Host | example/demo | Bare bones MCP fastmcp_quickstart.py example fails out of the box in l |
| 1560 | Host | unknown | Usage Error |
| 1585 | Host | transport/connection | FastMCP import fails after httpx≥0.28 upgrade (TransportError removed) |
| 1970 | Host | discovery/routing | Cannot find reference 'MCPServer' in 'mcp.server.mcpserver'  in Quicks |
| 2233 | Host | transport/connection | pywin32 installation fails on Windows — hard dep only needed for clien |
| 2543 | Host | transport/connection | Pin `httpx<1.0` (or similar upper bound) — `pip install --pre` resolve |
| 2826 | Host | protocol/spec | `simple-auth` is not working as expected |
| 76 | Server | transport/connection | GitHub MCP server doesn't work in Python SDK |
| 92 | Server | discovery/routing | Resource Templates not exposed to Claude UI |
| 178 | Server | discovery/routing | Log_level DEBUG breaks when creating a resource. |
| 263 | Server | discovery/routing | dynamic resource not working in Claude desktop |
| 291 | Server | discovery/routing | MCP Python client fails to load the server |
| 310 | Server | transport/connection | Unable to connect to mcp server |
| 320 | Server | external-dependency | Python client not working with mcp/puppeteer |
| 355 | Server | lifecycle/concurrency | Type error when using Lifespan context |
| 389 | Server | serialisation/parsing | Throwing an error when the function takes too long, TypeError: 'NoneTy |
| 396 | Server | transport/connection | MCP Server: Inconsistent Exception Handling in @app.call_tool and Clie |
| 399 | Server | protocol/spec | [Progress] ProgressNotification The message field is missing. |
| 402 | Server | transport/connection | Claude throwing an error "Server disconnected" |
| 406 | Server | external-dependency | MCP python server doesn't work in claude desktop app |
| 407 | Server | transport/connection | Error: Timed out while waiting for response to ClientRequest. Waited 0 |
| 491 | Server | discovery/routing | subscribe_resource return NotImplementedError |
| 511 | Server | protocol/spec | Unable to add annotations data with @FastMCP.tool() decorator |
| 514 | Server | transport/connection | FastMCP server with SSE transport fails to shut down on a signal |
| 537 | Server | transport/connection | Tool.from_function fails to detect parameterized Context subclasses |
| 560 | Server | environment/packaging | Failed to run server: module 'mcp' has no attribute 'run' |
| 608 | Server | environment/packaging | AttributeError: module 'mcp' has no attribute 'prompt' |
| 647 | Server | transport/connection | Bugs in simple-streamablehttp-stateless |
| 671 | Server | transport/connection | MCP Tool execution hangs indefinitely in stdio mode when calling exter |
| 688 | Server | serialisation/parsing | After "uv run mcp" getting TypeError: Parameter.make_metavar() missing |
| 776 | Server | error handling/reporting | Misleading warning for progress callback exceptions |
| 790 | Server | transport/connection | MCP servers can not be accessed via Docker and docker-compose anymore. |
| 793 | Server | example/demo | The official example code does not work |
| 872 | Server | discovery/routing | Mounting ASGI apps with a different named routes |
| 883 | Server | transport/connection | AssertionError: Unexpected message while using middlewares |
| 932 | Server | transport/connection | `simple-tool` exiting error |
| 949 | Server | example/demo | Bug in the simple-auth server example |
| 1084 | Server | example/demo | An error exists in the elicitation example |
| 1095 | Server | transport/connection | Multiple bugs in `mcp` library related to async context management |
| 1101 | Server | transport/connection | Running into an `ImportError` when executing the MCP client in `exampl |
| 1160 | Server | serialisation/parsing | MCP cannot process fastapi JSONResponse |
| 1220 | Server | lifecycle/concurrency | Task Group inialization error on lifespan and mounting on FastMcp |
| 1272 | Server | transport/connection | Server hangs when shutting down if a connection is still open |
| 1278 | Server | transport/connection | StdioServerTransport Fails to Invoke Tool Handlers on Linux (Python SD |
| 1372 | Server | lifecycle/concurrency | fastmcp.run() runtimeerror: task group is not initialized. make sure t |
| 1482 | Server | serialisation/parsing | Unable to call context.elicit(msg, schema) (using /examples/elicitatio |
| 1487 | Server | transport/connection | Bug: Calculator server fails with ModuleNotFoundError in mcp.server.tr |
| 1768 | Server | error handling/reporting | UrlElicitationRequiredError not thrown as an McpError exception |
| 1967 | Server | lifecycle/concurrency | ClosedResourceError During MCP Stateless Server Shutdown When Sending  |
| 2156 | Server | transport/connection | MCPServer.add_tool() missing `execution` parameter for task support de |
| 2429 | Server | transport/connection | [v1.x] Server-side outputSchema validation blocks tool error reporting |
| 2527 | Server | transport/connection | FastMCP.__init__ clobbers root logger with INFO RichHandler — hangs st |
| 2663 | Server | transport/connection | FastMCP.run(transport="stdio") produces noisy traceback on KeyboardInt |
| 2695 | Server | environment/packaging | Dead code path in MCPServer._handle_call_tool and incorrect call_tool  |
| 2702 | Server | transport/connection | FastMCP: streamable_http_app() silently breaks when BaseHTTPMiddleware |
| 2961 | Server | discovery/routing | [Bug] ResourceTemplate.matches() does not escape regex special chars i |
| 2965 | Server | protocol/spec | [Bug] check_capability does not validate elicitation sub-capabilities  |
| 3123 | Server | serialisation/parsing | Image content blocks >99 bytes fail with "illegal base64 at byte 0" |
| 3216 | Server | protocol/spec | URI templates does not work with Inspector v2 |
| 3353 | Server | serialisation/parsing | 2025-11-25 `Tool.inputSchema`/`outputSchema` reject boolean sub-schema |
| 3434 | Server | protocol/spec | In-process callback failures break tool calls and notification sends |
| 3649 | Server | protocol/spec | MCPServer completion handler returning more than 100 values fails on 2 |
| 101 | Transport | transport/connection | SSE client connect SSE Server got Error: " Error in post_writer" and " |
| 196 | Transport | transport/connection | Tools list RuntimeError with SSE transport |
| 238 | Transport | transport/connection | multiple servers deployment occur error |
| 256 | Transport | transport/connection | fastmcp SSE mode cannot be connected |
| 283 | Transport | transport/connection | Clients fail and crash If initial GET request returns a redirect (e.g. |
| 290 | Transport | serialisation/parsing | Expected ',' or ']' after array element in JSON in every MCP-Response |
| 390 | Transport | transport/connection | MCPv1.6.0 - SSE Initialization Hang with FastMCP - 202 Accepted |
| 398 | Transport | transport/connection | Connect to MCP Server with SSE  Invalid transport type: undefined |
| 432 | Transport | transport/connection | SSE Connection Failure Described as "throw new Error("Not connected")" |
| 433 | Transport | transport/connection | SSE Connection Failure Described as "throw new Error("Not connected")" |
| 447 | Transport | transport/connection | sse_client blocks indefinitely when server has incorrect base URL |
| 464 | Transport | transport/connection | Wrong data path when MCP server mounted as ASGI SSE app under some sub |
| 469 | Transport | transport/connection | sse_client connect to mcp server got server error 504 |
| 490 | Transport | transport/connection | SSE MCP server fails when URL contains subpaths |
| 492 | Transport | protocol/spec | `post_writer` Client error `400 Bad Request` when initializing session |
| 503 | Transport | transport/connection | Unable to work properly with SSE transport when perform long time task |
| 507 | Transport | transport/connection | 404 Not Found Error when Establishing SSE Connection via MCP Python SD |
| 530 | Transport | transport/connection | VSCode cannot connect? Failing with `405 Method Not Allowed` |
| 563 | Transport | transport/connection | `sse_client` fails if URL is not on the root path |
| 585 | Transport | transport/connection | Python MCP SDK: Incorrect handling of absolute paths in SSE endpoint U |
| 613 | Transport | auth/credentials | 401 from /sse after upgrading to 1.7.0 |
| 617 | Transport | transport/connection | SSE not working with 'https' endpoint |
| 680 | Transport | transport/connection | Streamable HTTP hangs forever when the server attempts any callback |
| 701 | Transport | transport/connection | StreamableHttp  Server send notify invalid |
| 705 | Transport | transport/connection | SSE client doesn't raise exception if the MCP server responds with tex |
| 733 | Transport | transport/connection | SSE does not work on nested routes |
| 783 | Transport | transport/connection | mount_path does not work with sse_app |
| 789 | Transport | transport/connection | mcp-simple-streamablehttp-stateless not working as expected |
| 1010 | Transport | transport/connection | BUG REPORT: HTTP errors are being silently swallowed in the Streamable |
| 1051 | Transport | transport/connection | Bug Report: StreamableHTTP GET Requests Fail with "Bad Request: Missin |
| 1053 | Transport | transport/connection | Streamable HTTP transport fails when accessing MCP server on Cloud Run |
| 1070 | Transport | transport/connection | Unexpected connection closed |
| 1072 | Transport | transport/connection | Errors with Streamble HTTP |
| 1079 | Transport | transport/connection | Missing OPTIONS handler for Streamable HTTP |
| 1081 | Transport | transport/connection | Unexpected behavior of streamable-http transport on public server |
| 1144 | Transport | transport/connection | streamable_http client call_tool hangs when receiving invalid JSONRPCM |
| 1190 | Transport | transport/connection | MCP server in the HTTP Streamable mode broken |
| 1218 | Transport | transport/connection | `simple-streamablehttp-stateless` example will not return data if `id= |
| 1219 | Transport | discovery/routing | _handle_stateless_request  ClosedResourceError |
| 1274 | Transport | transport/connection | Streamable HTTP client performance regression starting with v1.12.0 |
| 1367 | Transport | transport/connection | Mounting a Streamable HTTP MCP endpoint on existing FastAPI app does n |
| 1437 | Transport | transport/connection | SSE Hangs After Disconnect |
| 1450 | Transport | transport/connection | Response leak in SSE handlers |
| 1764 | Transport | transport/connection | Race condition in StreamableHTTP: zero-buffer memory streams cause dea |
| 1811 | Transport | transport/connection | client's `read_stream_writer` open after SSE disconnection hanging `.r |
| 1835 | Transport | transport/connection | Http errors are not handled properly by streamable_http |
| 1941 | Transport | transport/connection | streamable_http client hangs indefinitely when connecting to POST-only |
| 2110 | Transport | transport/connection | HTTP transport swallows non-2xx status codes causing client to hang |
| 2232 | Transport | transport/connection | streamable_http_client hangs indefinitely when server sends POST-only  |
| 2375 | Transport | transport/connection | Harcoded Content-Type in the client cannot be overriden |
| 2454 | Transport | transport/connection | stdio_client crashes on malformed UTF-8 from child stdout instead of s |
| 2546 | Transport | transport/connection | Bug: stdio transport fails to handle Content-Length header format from |
| 2583 | Transport | transport/connection | Race condition between SSE session init and tools/call rejection (-326 |
| 2604 | Transport | transport/connection | streamable_http_client: one concurrent request HTTPStatusError tears d |
| 2655 | Transport | transport/connection | Streamable HTTP server silently drops in-flight request when client re |
| 2688 | Transport | transport/connection | `TransportSecuritySettings.allowed_hosts=[]` (default) silently reject |
| 2727 | Transport | auth/credentials | streamable_http client does not send `Origin` header → rejected with 4 |
| 2751 | Transport | transport/connection | Deep JSON-RPC request over stdio logs a validation error and leaves th |
| 2848 | Transport | serialisation/parsing | Invalid JSON-RPC envelope errors are not correlated with the original  |
| 2958 | Transport | transport/connection | StreamableHTTP server accumulates CLOSE_WAIT sockets behind reverse pr |
| 3060 | Transport | transport/connection | streamable HTTP (stateful): concurrent requests with duplicate JSON-RP |
| 3091 | Transport | auth/credentials | streamable_http: HTTP status errors (401/403/5xx) on tools/list, tools |
| 3102 | Transport | transport/connection | Streamable HTTP server never returns the spec-mandated 405 for GET req |
| 3150 | Transport | transport/connection | [v1.x] Backport #1912 and cut a release: a non-UTF-8 POST body on Stre |
| 3228 | Transport | transport/connection | Rejected streamable-HTTP requests leave live sessions behind: the sess |
| 3281 | Transport | transport/connection | streamable_http (legacy mode): early response.aclose() discards a TCP  |
| 3335 | Transport | transport/connection | Windows MCP SSH stdio transport closes after initialize when PROGRAMDA |
| 3356 | Transport | transport/connection | bug(client/streamable_http): prevent infinite SSE reconnect loops with |
| 3469 | Transport | transport/connection | StreamableHTTP: a client disconnect while reading the POST body is log |
| 3492 | Transport | transport/connection | Streamable HTTP stateless servers hang clients on the listen-mode GET  |
| 3496 | Transport | transport/connection | Windows stdio resolves .ps1 then fails to spawn it |
| 3503 | Transport | transport/connection | streamable HTTP client: the standalone GET stream advertises Accept: a |
| 3504 | Transport | transport/connection | Does same-origin redirect enforcement break MCP servers behind a rever |
| 3522 | Transport | transport/connection | Streamable HTTP client stays closed after an interrupted response and  |
| 3551 | Transport | transport/connection | stdio server ignores the first two Ctrl+C presses at a terminal (block |
| 3588 | Transport | transport/connection | Streamable HTTP: Client mode="auto" fails on server/discover against M |
| 3616 | Transport | transport/connection | SSE: a POST blocks forever (and SIGTERM hangs) when the server lifespa |
| 3631 | Transport | transport/connection | Streamable HTTP notification triggers duplicate response after HTTP 20 |
| 3639 | Transport | transport/connection | Streamable HTTP client hangs on a null-id JSON-RPC error in a 200 JSON |
| 3641 | Transport | transport/connection | ClosedResourceError + 'Unexpected ASGI message ... after response alre |

## Prose

For the 293 active bugs we could not reproduce, we still classify the fault NATURE from each issue's description (there is no runtime evidence). This is a description-based nature taxonomy, distinct from the exposure channel (which needs runtime evidence) and deliberately independent of the Taraghi taxonomy. Only natures that are determinable from the description are assigned; 2 ambiguous bugs are left unclassified rather than guessed.