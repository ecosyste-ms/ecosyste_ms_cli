# MCP server — exploratory testing findings

Session against `feature/mcp2` (commit `7d42f85`, mcp 2.2.0). Time-boxed, 20
findings. Scope was the MCP surface only: tool listing, tool-name routing,
input-schema generation, and result/error handling in
[`ecosystems_cli/mcp_server.py`](../ecosystems_cli/mcp_server.py).

**None of these are regressions from the mcp 2.x migration.** Every one of them
is either pre-existing behaviour carried over unchanged, or a gap the 2.x API
newly lets us close. Where the migration is relevant, it is noted.

Probes were run offline against synthetic specs (to isolate logic) and against
the 17 vendored specs (to size real impact), plus a live stdio session with an
mcp 2.x client for the protocol-level items.

## Summary

| # | Finding | Severity | Live or latent |
|---|---|---|---|
| 1 | Duplicate `operationId` merges parameters from every matching path | High | Latent |
| 2 | Falsy API results are all reported as "No data returned" | High | **Live** |
| 3 | `requestBody` schema is discarded; clients get an opaque `body` object | High | **Live** |
| 4 | Generic `_call` accepts a missing `operation` and sends `None` upstream | Medium | **Live** |
| 5 | Unknown tool names produce a misleading "Unknown API" message | Medium | **Live** |
| 6 | Exceptions with empty messages yield a bare `Error:` | Medium | **Live** |
| 7 | Trailing-underscore tool name sends an empty operation upstream | Medium | Latent |
| 8 | An `operationId` of `call` would collide with the generic tool | Medium | Latent |
| 9 | Array parameters lose `items`; enums lose `enum` | Medium | **Live** |
| 10 | No local validation of required arguments; upstream round-trip wasted | Medium | **Live** |
| 11 | Wrong-typed argument surfaces as an opaque upstream 500 | Medium | **Live** |
| 12 | Undeclared/typo'd arguments are silently dropped | Medium | **Live** |
| 13 | `EcosystemsCLIError` is re-raised as a bare `Exception` | Low | **Live** |
| 14 | Path-level OpenAPI `parameters` are ignored | Low | Latent |
| 15 | `$ref` parameters produce a `None` property key | Low | Latent |
| 16 | Non-JSON `requestBody` yields `body` required but undeclared | Low | Latent |
| 17 | Parameters with no `schema` are silently typed as `string` | Low | **Live** |
| 18 | `tools/list` is a 71 KB payload across 164 tools | Low | **Live** |
| 19 | 8 tools advertise an empty `properties` schema | Info | **Live** |
| 20 | `tools/list` ignores pagination entirely | Info | **Live** |

---

## High

### 1. Duplicate `operationId` merges parameters from every matching path

In `_call_tool`, the spec scan breaks out of the inner method loop but not the
outer path loop, so every path whose operation matches contributes parameters.

```python
r = await call("packages_dup", {"id": "1", "q": "z"}, spec)
# paths: /a/{id} (path param id), /b (query param q), both operationId "dup"
# => _call_api('packages', 'dup', {'id': '1'}, {'q': 'z'}, {})
```

Arguments intended for one operation leak into the call for another. The `break`
at the end of the match block reads as "stop at the first match" but does not.

No vendored spec currently has a duplicate `operationId`, so this is latent — but
it is invisible if it ever appears, because the call still succeeds.

### 2. Falsy API results are all reported as "No data returned"

`result_text = json.dumps(result) if result else "No data returned"` treats every
falsy value as absent data:

| API returns | Client sees |
|---|---|
| `{}` | `No data returned` |
| `[]` | `No data returned` |
| `0` | `No data returned` |
| `false` | `No data returned` |
| `""` | `No data returned` |

`[]` is the common one: "the query ran and matched nothing" is a real, useful
answer, and it is indistinguishable here from "something went wrong upstream".
`0` and `false` are legitimate scalar responses reported as no data at all.

Observed live, not just in theory:

```
call_tool("packages_lookupPackage", {"purl": "pkg:npm/üüü…"})
  -> "No data returned"   is_error=False
```

An LLM client reading that cannot tell an empty result set from a failure.

### 3. `requestBody` schema is discarded; clients get an opaque `body` object

`_build_input_schema` records that a body exists but throws away its shape:

```python
# spec: body is an object with required ["name"] and typed properties
t.input_schema["properties"]["body"]
# => {'type': 'object', 'description': 'Request body'}
```

The client is told to send "an object" with no indication of which fields, which
are required, or their types. For an LLM-driven client this is close to
unusable: it has to guess the body shape.

Affects 19 tools: the 17 generic `{api}_call` passthroughs plus the two real
body-taking operations, `issues_createJob` and `packages_bulkLookupPackages`.

## Medium

### 4. Generic `_call` accepts a missing `operation` and sends `None` upstream

The generic tool's own schema declares `"required": ["operation"]`, but nothing
enforces it:

```python
await call("packages_call", {})
# => _call_api('packages', None, {}, {}, {})
```

`None` reaches `api_factory.call(operation_id=None)`. The server declares a
contract it does not check.

### 5. Unknown tool names produce a misleading "Unknown API" message

The SDK does not verify that a called tool was actually advertised, so unknown
names reach the handler and are parsed as `{api}_{operation}`:

```
call_tool("totally_made_up", {}) -> "Unknown API: totally"   is_error=True
```

The error names a nonexistent API rather than saying the tool does not exist,
which points a debugging client at the wrong thing. Worth handling explicitly
now that `is_error` exists to carry a proper message.

### 6. Exceptions with empty messages yield a bare `Error:`

`f"Error: {str(e)}"` loses the exception type, so an exception with no message
produces no information at all:

| Raised | Client sees |
|---|---|
| `ValueError("bad")` | `Error: bad` |
| `KeyError("k")` | `Error: 'k'` |
| `RuntimeError("")` | `Error: ` |
| `Exception()` | `Error: ` |

Including `type(e).__name__` would cost nothing and make the last two
actionable.

### 7. Trailing-underscore tool name sends an empty operation upstream

`"packages_"` splits into a valid API and an empty operation, and is dispatched:

```
_call_tool("packages_", {}) -> _call_api('packages', '', {}, {}, {})   is_error=False
```

Compare `"packages"` (no separator), which is correctly rejected as
`Invalid tool name`. The empty-operation case should be rejected the same way.

### 8. An `operationId` of `call` would collide with the generic tool

Tool names are `{api}_{operationId}`, and the generic passthrough is
`{api}_call`. An upstream operation named `call` collides:

```python
# spec with operationId "call" in the packages API
len([t for t in tools if t.name == "packages_call"])   # => 2
```

Two tools share a name, and because `_call_tool` checks `name.endswith("_call")`
first, the generic branch always wins — the real operation becomes unreachable.

Near misses are safe: `packages_recall` does not end in `_call` and routes
correctly. Only the exact name `call` collides. Latent today, and cheap to guard
by reserving the name when building the list.

### 9. Array parameters lose `items`; enums lose `enum`

`_build_input_schema` copies only `type` and `description` out of the parameter
schema:

| Spec parameter | Generated schema |
|---|---|
| `{type: array, items: {type: string}}` | `{type: array, description: ""}` |
| `{type: string, enum: [a, b]}` | `{type: string, description: ""}` |

An `array` with no `items` is rejected by strict JSON Schema validators, and a
dropped `enum` removes exactly the constraint that would stop a client guessing
an invalid value. No vendored spec currently uses either, so nothing is broken
today — but the fidelity loss is unconditional and will bite whenever upstream
adds one.

### 10. No local validation of required arguments

Omitting a required parameter is not caught locally; the request goes out and
fails upstream:

```
call_tool("packages_getRegistryPackage", {})
  -> "Error: API Error: Missing required parameter: registryName, packageName"
```

The schema needed to reject this before the network call is already built and
advertised. Worth confirming this is intentional — deferring to the API is a
defensible choice, it is just currently implicit.

### 11. Wrong-typed argument surfaces as an opaque upstream 500

```
call_tool("packages_getRegistries", {"page": "not-a-number"})
  -> "Error: API Error: Server error: {"error":"internal server error"}"
```

A client-side type error is reported as an upstream internal error, which sends
whoever is debugging to the wrong system. The declared schema says
`page: integer`.

### 12. Undeclared/typo'd arguments are silently dropped

```python
await call("packages_op", {"pge": 5})   # "page" misspelled
# => _call_api('packages', 'op', {}, {}, {})
```

Confirmed live too: `{"bogus_param": "x", "per_page": 1}` returns a normal
successful result. The call silently does something other than what was asked,
with no signal. For a self-correcting LLM client, silence is the worst outcome —
it has no way to learn it got the name wrong.

### 13. `EcosystemsCLIError` is re-raised as a bare `Exception`

```python
raise Exception(f"API Error: {str(e)}")
# isinstance(e, EcosystemsCLIError) -> False
```

The type is flattened, so no caller upstream can catch the specific error. It is
only ever caught by the blanket `except Exception` in `_call_tool` today, which
is why this is low severity rather than medium.

## Low

### 14. Path-level OpenAPI `parameters` are ignored

OpenAPI allows `parameters` on the path item, shared by all its operations.
`_build_input_schema` reads only `operation["parameters"]`, so path-level ones
never appear in a tool schema, and `_call_tool` never routes them.

No vendored spec uses path-level parameters (checked all 17), so this is latent.

### 15. `$ref` parameters produce a `None` property key

A `$ref`'d parameter has no inline `name`, and `param.get("name")` returns
`None`, which is used as a dict key:

```python
t.input_schema["properties"]   # => {None: {'type': 'string', 'description': ''}}
```

That is not valid JSON Schema and would serialize as a `null` key. No vendored
spec uses `$ref` parameters, so latent — but note the failure is silent rather
than an error.

### 16. Non-JSON `requestBody` yields `body` required but undeclared

`body` is appended to `required` based on `requestBody.required`, but only added
to `properties` when the content type is `application/json`:

```
required: ['body']   properties: []
```

A schema requiring a property it does not declare. Both real body-taking
operations are JSON, so latent.

### 17. Parameters with no `schema` are silently typed as `string`

`param.get("schema", {}).get("type", "string")` means a parameter with a missing
or unrecognised schema is advertised to clients as a string with no signal that
the type was assumed rather than read.

### 18. `tools/list` is a 71 KB payload across 164 tools

Measured: 71.4 KB serialized, 164 tools. That lands in the client's context on
every session. The 17 generic `{api}_call` tools overlap heavily with the 147
specific ones, so there is an obvious lever here if context budget matters —
worth a deliberate decision rather than a default.

## Info

### 19. 8 tools advertise an empty `properties` schema

`advisories_getAdvisoriesPackages`, `advisories_getSources`,
`dependabot_getPackageEcosystems`, `docker_usage`,
`opencollective_getProjectPackages`, and three others take no parameters. The
generated schema is `{"type": "object", "properties": {}, "required": []}`, which
is correct — recorded only to confirm it is intended rather than a spec-parsing
miss.

### 20. `tools/list` ignores pagination entirely

`_on_list_tools` accepts `PaginatedRequestParams` and ignores it, returning all
164 tools with `next_cursor=None`. Fine at this size and an explicit choice in
the migration; noted because the 2.x signature now makes the option visible, and
it interacts with finding 18.

---

## What was checked and found clean

- **Tool-name uniqueness** — no duplicates across all 164 tools from the 17
  vendored specs.
- **Name round-tripping** — every non-generic tool name splits back into a known
  API and an operation.
- **Schema wellformedness on real specs** — no `required` entry missing from
  `properties`, no duplicate `required` entries, no `None` property keys, no
  array parameter missing `items`, no empty tool descriptions.
- **Concurrency** — 5 concurrent `tools/call` requests all succeeded in 0.5s,
  confirming the `asyncio.to_thread` offload keeps the event loop responsive.
- **Unicode and long arguments** — a 200-character non-ASCII `purl` round-tripped
  without encoding errors (the result was reported via finding 2).
- **Error containment** — every failure path returns a result rather than
  raising through the transport; no probe crashed the server or broke the
  session.

## Suggested triage

Findings 2, 3, 5, 6 and 12 are the ones that degrade an LLM client's ability to
use this server correctly, and all five are small, self-contained fixes. Finding
1 is the one most worth fixing before it can ever trigger, since it fails
silently and produces a plausible-looking wrong call.
