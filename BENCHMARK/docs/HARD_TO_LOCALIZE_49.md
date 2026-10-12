# Hard-to-localise reasons (49 reproduced bugs)

> Induced from each bug's actual reported error (evidence), not from a preset category. Data: `data/full_pool/hard_to_localize_49.json`.

| Issue | Origin (start) | Exposure (channel) | Hard-to-localise reason | Evidence |
|---|---|---|---|---|
| 110 | Client | pushed-server | genericised | Error executing tool bad, is_error=True; real cause = non-UTF-8 bytes decode |
| 1361 | Client | pushed-server | genericised | Error executing tool boom, is_error=True |
| 2057 | Client | silent | silent-ok | HTTP 202; null-id accepted as notification, never rejected |
| 2114 | Client | pushed-server | genericised | Error executing tool boom, is_error=True |
| 3572 | Host | pushed-server | genericised | real_r_validation_echo_input.txt: Error executing tool lookup, is_error=True |
| 3579 | Host | pushed-server | insufficient | real_r_empty_server_components.txt: Unknown tool, is_error=True |
| 3637 | Host | pushed-server | genericised | real_r_flat_argument.txt: Error executing tool summarize, is_error=True |
| 3646 | Host | silent | silent-ok | real_r_extra_arg_silent.txt: extra arg -> 1, is_error=False |
| 234 | Server | single-layer-correct | insufficient | Unknown tool: no_such_tool, is_error=True |
| 244 | Server | registration-error | registration | RAISED-AT-REG ValueError: URI template variables missing |
| 348 | Server | single-layer-masked | genericised | Error executing tool img (real PydanticSchemaGenerationError hidden) |
| 417 | Server | single-layer-masked | genericised | Error executing tool boom |
| 698 | Server | single-layer-masked | genericised | Error executing tool boom |
| 743 | Server | single-layer-masked | genericised | Error executing tool boom |
| 891 | Server | single-layer-masked | genericised | Error executing tool f (real TypeError hidden) |
| 1060 | Server | single-layer-masked | genericised | Error executing tool img |
| 1579 | Server | single-layer-correct | insufficient | RAISED MCPError: Unknown resource |
| 1702 | Server | single-layer-masked | genericised | Error executing tool get_name |
| 1974 | Server | registration-error | registration | RAISED-AT-REG AttributeError: Handler has no __name__ |
| 2153 | Server | single-layer-masked | genericised | Error executing tool boom |
| 2386 | Server | single-layer-masked | genericised | Error executing tool boom (CWE-209 sensitive value hidden) |
| 2422 | Server | single-layer-correct | insufficient | Unknown tool: no_such_tool, is_error=True |
| 2431 | Server | single-layer-masked | genericised | Error executing tool boom (McpError not pickle-safe) |
| 2539 | Server | silent | silent-ok | {"text": null}, is_error=False; wrong result shape returned |
| 2770 | Server | single-layer-masked | genericised | Error executing tool boom |
| 3067 | Server | silent | silent-ok | call_tool(add,{typo:9}) -> 3, is_error=False; extra param silently dropped |
| 3099 | Server | single-layer-masked | genericised | Error executing tool ext |
| 3266 | Server | single-layer-masked | genericised | Error executing tool boom |
| 3341 | Server | single-layer-correct | genericised | RAISED RuntimeError: Invalid structured content (nan) |
| 3342 | Server | single-layer-correct | genericised | RAISED MCPError: Internal server error |
| 3351 | Server | single-layer-correct | genericised | Error executing tool f: 1 validation error (detail retained) |
| 3385 | Server | single-layer-correct | genericised | RAISED RuntimeError: Invalid structured content (inf) |
| 3549 | Server | silent | silent-ok | real_r_race_lost_update.txt: 20 concurrent calls -> result 1, is_error=False (lost update) |
| 3554 | Server | single-layer-masked | genericised | real_r_bytes_output_crash.txt: Error executing tool get_bytes |
| 3569 | Server | single-layer-masked | genericised | real_r_permission_swallow.txt: Error executing tool fragile2 |
| 3573 | Server | registration-error | registration | real_r_iterator_meta_fail.txt: RAISED-AT-REG PydanticSchemaGenerationError |
| 3578 | Server | silent | silent-ok | real_r_duplicate_tool_shadow.txt: dup tool shadow -> 2, is_error=False |
| 3585 | Server | silent | silent-ok | real_r_media_unregistered_mime.txt: image/jpg, is_error=False (unregistered mime accepted) |
| 3586 | Server | single-layer-masked | genericised | real_r_non_tool_error_silent.txt: Error executing tool fragile |
| 3592 | Server | silent | silent-ok | real_r_fallback_success_flag.txt: stale-cache-fallback, is_error=False |
| 3640 | Server | silent | silent-ok | real_r_capabilities_drop.txt: is_error=False; advertised capabilities dropped |
| 3643 | Server | silent | silent-ok | real_r_userlist_prompt.txt: is_error=False; PromptMessage stringified |
| 3644 | Server | single-layer-correct | genericised | real_r_outputschema_mode.txt: RAISED RuntimeError invalid structured content |
| 3656 | Server | single-layer-masked | genericised | Error executing tool a |
| 2618 | Transport | silent | silent-ok | HTTP 200; MCP-Protocol-Version header vs body mismatch not validated |
| 2741 | Transport | pushed-server | genericised | Error executing tool boom, is_error=True; real cause only in "Session crashed" log |
| 3556 | Transport | caller-exception | caller-exception | real_r_session_reinit_404.txt: RAISED ExceptionGroup |
| 3557 | Transport | caller-exception | caller-exception | real_r_jsonrpc_error_code.txt: HTTP 400, JSON-RPC -32602 |
| 3560 | Transport | caller-exception | caller-exception | real_r_tool_timeout.txt: RAISED ExceptionGroup (timeout) |

## Distribution

- 28: genericised
- 11: silent-ok
- 4: insufficient
- 3: registration
- 3: caller-exception

## Prose

Reading the reported error of each of the 49 reproduced bugs, we ask why it is hard to localise. The reasons converge into a small set. The dominant one is that a generic message replaces the real root cause (e.g. `Error executing tool X`, `Internal server error`, `Invalid structured content`), so even when the bug is reported at the correct layer the precise cause is erased. A second class is fully silent: the SDK returns a success / no-error result (`is_error=False`, HTTP 200, or a plausible value) despite a logical error. A smaller set surfaces as a bare caller-side exception outside the server context, or reports only a vague `Unknown X` with no precise cause, and a few fail at registration time before the server can start.
