# Runtime contract

## Inputs

Supply the actual host and model, a provider or explicitly federated selection, one of six categories,
a query up to 240 characters and 1-5 results/provider. Downloads consume an unchanged signed search
result from the same state directory, runtime revision and host, less than one day old. Select result
and variant by zero-based index. Output paths must be new and outside the plugin package.

## Results

The signed search payload carries `utc`, `host`, `fingerprint`, `query`, `category`, `items` and `trace`.
Each asset has `provider`, `id`, `title`, `creator`, `source_page`, `license`, `license_url`,
`rights_status`, `category`, `variants`, `warnings`, `attribution` and `retrieved_utc`. Each variant
has an exact provider URL and label, with byte count or SHA-256 when advertised. No fictitious
`download_url`, transformed CDN hostname or blanket site licence is accepted.

Downloads add selected variant, local path, SHA-256, byte count, response headers, decoded dimensions
or audio/video properties, rights-review note, SA choice and `technical_test_only`. Since 0.3.0 the sidecar
also records `host`, `model`, `runtime_version`, the runtime `fingerprint`, `search_utc`, `search_query`,
the caller's `task_id` (or null), `trace_sha256` and `hash_source` (`provider` when the provider
advertised a SHA-256 that matched, otherwise `local_only`). These fields are additive; existing keys
keep their meaning. Save the sidecar
with the file. The sidecar is provenance, not a model/property release or a guarantee of copyright.

## Task envelope

Every command accepts `--envelope-out <new file>`, `--task-id`, `--requester name@version` and `--owner`.
The envelope is a `framecore-task-result/1` document defined by
[the shared schema](../../../contracts/framecore-task.schema.json); stdout is unchanged. It lists the
signed search file as input, the media file and its sidecar as outputs with SHA-256 and bytes, the
asset licence/attribution block, decode and hash evidence, warnings, errors and checks that did not run
(listening or visual review, reading the licence page). `status` is `succeeded`, `refused` (a policy or
rights gate), `blocked` (missing decoder) or `failed`. Without `--task-id` the envelope is marked
`standalone`. The envelope path must be new and outside the package; it is checked before any request.
Callers find the operations and flags in [capabilities.json](../../../capabilities.json).

A `--technical-only` verification proves transport and decoding only. It never unlocks a later
production `download` for that host, provider and category.

## Rights

| Status | Normal download |
| --- | --- |
| eligible | Explicit CC0/PDM or supported CC BY with attribution |
| review_sa | User must deliberately accept SA and its obligations |
| review_nasa | User-supplied item/use-specific review of NASA restrictions |
| review_jurisdiction | User-supplied text and recording rights evidence for the intended jurisdiction |
| blocked | Refused; never reinterpret Unknown, NC or ND as permission |

Only providers with reviewed applicable terms and confirmed Work media paths are packaged.
Unknown provider IDs are refused before any network request. Documented fair-use rules and
conservative pacing apply even when a provider publishes no numeric quota. One category's test never certifies another media category.

## Errors, pacing and cache

Exit 0 means the command completed, not that every result is commercially cleared. Exit 2 produces
JSON with `status`, `error`, `message`, request `trace` and `next_action`. The complete error codes:

- Request and policy: `unknown_provider`, `policy_hold`, `invalid_model`, `missing_hypothesis`,
  `input_limit`, `unsupported_category`, `invalid_index`, `host_mismatch`, `host_not_verified`,
  `rights_blocked`, `daily_quota`, `busy`.
- Provenance and outputs: `untrusted_result`, `stale_result`, `result_size`, `output_exists`,
  `package_output`, `provider_mismatch`.
- Network: `unsafe_url`, `unapproved_host`, `request_budget`, `redirect_limit`, `cloudflare_challenge`,
  `access_denied`, `rate_limited`, `server_error`, `http_error`, `transport_error`, `html_response`,
  `invalid_json`, `api_error`, `size_limit`, `size_or_time_limit`.
- Files and decoding: `hash_mismatch`, `size_mismatch`, `wrong_media_type`, `decoder_missing`,
  `unsupported_media`, `not_media`, `decode_failed`, `pixel_limit`, `archive_limit`, `archive_crc`,
  `unsupported_archive`.
- Envelope: `invalid_envelope` (the envelope did not match the schema and was not written).
- Anything else at the CLI boundary: `invalid_input_or_response`.

No automatic retry. A manually considered retry is limited to one additional attempt for a transient
failure, with a named hypothesis and provider Retry-After respected. No challenge/auth/rate bypass.
There is no source failover. Failed federated searches return their executed trace; other providers
are not queried after the failure. Preserve that failure when discussing alternatives.

JSON caching is keyed by exact URL and Accept header, uses cache-control max-age (capped at one day),
honors no-store/no-cache/private and may revalidate stale entries with ETag. `--fresh` bypasses it for
verification. Media is an explicitly requested local output, not a shared HTTP cache. Keep all
provider calls serial, at least one second apart. The state lock prevents concurrent local processes;
a lock left by a killed process requires inspection before removal, not repeated polling or bypass.

## Cross-host behavior

Three manifests identify one package/version. Claude uses the repository marketplace; ChatGPT uses
the complete private plugin package; Codex uses its compatibility manifest. The shared Python CLI
uses no remote MCP server, account, paid backend or generated browser session. Public GET requests
leave the host; downloaded media stays local until an independently authorized delivery.

Readiness evidence is local and short-lived. A host label is explicitly declared by the executing
agent. Never forge a Claude label in Work, move host proofs to another machine, or claim a package
test proves active-client registration. Missing shell/network yields a plan and a named limitation.
