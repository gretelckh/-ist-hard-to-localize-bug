# Four-Layer MCP Runtime-Fault Taxonomy

MCP connects an LLM to external tools through four components. When a fault occurs, we
classify it by the architectural layer at which the fault **originates**. This is our primary
classification dimension because it is exactly what a developer needs to localize the fault
(and, as we show, the SDK often reports the error at a *different* layer).

## The four layers

| Layer | Label | Fault originates in ... | Representative injected cases |
|---|---|---|---|
| **Host scheduling layer** | `Host` | the Host / LLM caller | invoking a non-existent tool, missing/misspelled arguments, wrong argument types |
| **Client message layer** | `Client` | client-side JSON-RPC payload assembly | redundant params, wrong argument nesting, invalid enum values |
| **Server tool layer** | `Server` | inside the MCP Server tool's execution logic | division-by-zero, index-out-of-range, assertion, custom exception, oversized response, duplicate registration, permission denied |
| **Transport layer** | `Transport` | session- and message-passing layer | calling a tool after session close, cancelled in-flight request, invalid raw message, invoke before init |

## Exposure channels (how a non-Server fault actually surfaces)

Rather than a binary cross/single label, we characterise how each non-Server fault is
actually exposed by the SDK (observation-driven, from the raw return text):

- **Pushed-to-Server**: reported as `Error executing tool X` (`is_error=True`) at the Server
  tool-dispatch layer, though the true origin is an upstream Host/Client component.
- **Silent**: the SDK returns a successful status (`is_error=False`) with a plausible result,
  hiding the logical error.
- **Caller-exception**: the fault surfaces as a raw Python exception
  (`CancelledError`, `RuntimeError: Client must be used within an async context manager`,
  ...) in the calling code, escaping the MCP `is_error` channel. This is how the
  Transport-layer faults manifest.
- **Single-layer**: Server-origin explicit faults reported within their own layer.
- **No-evidence**: a run whose raw capture did not contain a usable SDK/exception record.

Generalised manifestation-root-cause mismatch = aligned with `pushed-to-Server` +
`caller-exception` (reported at a concrete layer different from origin): 34/48 = 70.8%.

## Silent-failure classification

A silent failure is a run where the SDK returns a successful status (`is_error=False`) despite
an underlying logical or execution error. We distinguish two kinds:

- **Structural silent (4/4 variants):** the SDK always hides this class of error, independent
  of the concrete input. These are the most dangerous because they are deterministic and
  invisible.
- **Input-dependent silent (1-3/4 variants):** the same root cause is silent for some inputs
  and raises an explicit error for others (e.g. a string is implicitly coerced, but `None`
  triggers `ValidationError`).

## Comparison with existing taxonomies (e.g. Taraghi et al.)

Existing log-based fault taxonomies (e.g. Taraghi and co-workers) classify failures by
*trigger type* (e.g. `Server/Host Configuration`, `Server/Tool Configuration`,
`General Programming`). We map every injected case to such a category for comparison.

The two taxonomies are **complementary**:
- Taraghi explains *what kind of bug* occurred (its nature/trigger).
- Ours explains *where it originated* and *how it is (mis)reported* (its location + the
  manifestation-root-cause separation).

Our taxonomy is the primary dimension because it directly supports fault localization and
observability — which prior taxonomies, focusing on trigger type *within* a layer, do not
express.

## Advanced "real-hard-bug" cases

The original 20 cases are synthetic, script-level faults. We additionally reproduce real-world
**hidden faults** that the MCP SDK often does not surface (see `faultcases/advanced/`):

| Case | Layer | Hidden behaviour observed |
|---|---|---|
| concurrent race on shared state | Host | silent (`is_error=False`), no error flag |
| slow tool / no timeout protection | Transport | silent (`is_error=False`), caller waits then gets success; only surfaces if the caller explicitly sets a timeout |
| duplicate tool registration | Server | SDK only WARNINGs + silently uses the FIRST registered version |
| cross-call state leakage | Server | content changes across calls, silent |
| stream / multi-step interruption | Server | dependent on prior-step artifact |
| concurrent unsynchronised increment | Host | silent, no error flag |

These illustrate that many production-grade MCP failures are **silent**, making them the
hardest to localize — a key motivation for our diagnosis study.