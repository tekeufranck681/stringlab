# StringLab — Technical Contract (v1)

**Stack:** FastAPI · PostgreSQL · SQLAlchemy ORM · React + TypeScript (TSX) · Tailwind CSS
**Status:** Locked for the build. Any change to a shape in this document must be agreed by the whole team because both sides build against it.

This contract is the single source of truth for the boundary between backend and frontend. It defines every data object, the `inputSpec` format, the trace/step schema that drives the animations, the full API surface (request **and** response for each endpoint), the error model, the session-cookie behaviour, and a concrete specification for all twelve operations. Code is intentionally excluded — these are the *data shapes and interface declarations* both halves implement against.

---

## 0. Conventions

| Topic | Decision |
|---|---|
| Base path | All endpoints are prefixed `/api/v1`. The `v1` lets a future contract change ship side-by-side. |
| Encoding | UTF-8 everywhere. Request and response bodies are `application/json`. |
| JSON casing | **API JSON uses `camelCase`.** This is idiomatic for the React/TS frontend. Pydantic serialises with a camelCase alias generator. |
| DB casing | **Database columns use `snake_case`** (e.g. `operation_id`, `created_at`). SQLAlchemy maps between the two; the frontend never sees snake_case. |
| Timestamps | ISO 8601 UTC strings with a trailing `Z`, e.g. `2026-06-12T09:30:00Z`. |
| Identifiers | Catalogue rows use integer surrogate keys but are addressed in the API by their stable **`slug`** (e.g. `/operations/kmp_search`). Runs are addressed by integer `runId`. |
| Empty/optional | Optional fields are omitted when absent rather than sent as `null`, except where a `null` is semantically meaningful (noted per field). |
| Session | Every request may carry the `sl_session` cookie; the backend issues one if absent. See §7. |
| Determinism | For identical inputs, an operation returns an identical `result` and `trace` (FR-3.5). |

---

## 1. Core Data Objects

These are the canonical shapes. Each appears below as a field table, a JSON example, and a TypeScript interface (the frontend's shared types).

### 1.1 Category

| Field | Type | Notes |
|---|---|---|
| `slug` | string | Stable machine name, e.g. `analysis` |
| `name` | string | Display title |
| `description` | string | One-line summary |
| `displayOrder` | integer | Ordering on the home screen |
| `operations` | Operation[] | Operations in this category (present in the catalog response) |

```json
{
  "slug": "search",
  "name": "Search & Matching",
  "description": "Locate a pattern within a text and report where and how often it occurs.",
  "displayOrder": 2,
  "operations": [ /* Operation objects */ ]
}
```

```ts
interface Category {
  slug: string;
  name: string;
  description: string;
  displayOrder: number;
  operations: Operation[];
}
```

### 1.2 Operation

| Field | Type | Notes |
|---|---|---|
| `slug` | string | Stable machine name, e.g. `kmp_search` |
| `name` | string | Display title |
| `categorySlug` | string | Parent category |
| `description` | string | What it does (FR-1.3) |
| `explanation` | string | Static "how it works" narrative (FR-1.3) |
| `inputSpec` | InputSpec | Field definitions for the input panel (FR-1.4) — see §2 |
| `complexity` | Complexity | `{ time, space }` big-O strings (FR-1.3) |
| `visualizationLevel` | enum | `"result"` \| `"step_log"` \| `"full"` (FR-5) |

```json
{
  "slug": "kmp_search",
  "name": "Knuth–Morris–Pratt Search",
  "categorySlug": "search",
  "description": "Find every position where a pattern occurs in a text in linear time.",
  "explanation": "KMP precomputes a failure table from the pattern so that, on a mismatch, it shifts the pattern by the longest reusable prefix instead of restarting — behaving like a deterministic finite automaton scanning the text.",
  "inputSpec": { /* see §2 */ },
  "complexity": { "time": "O(n+m)", "space": "O(m)" },
  "visualizationLevel": "full"
}
```

```ts
type VisualizationLevel = "result" | "step_log" | "full";
interface Complexity { time: string; space: string; }
interface Operation {
  slug: string;
  name: string;
  categorySlug: string;
  description: string;
  explanation: string;
  inputSpec: InputSpec;
  complexity: Complexity;
  visualizationLevel: VisualizationLevel;
}
```

### 1.3 Example

| Field | Type | Notes |
|---|---|---|
| `id` | integer | Example identifier |
| `label` | string | Display name, e.g. "Classic mismatch case" |
| `inputs` | object | Field values keyed by input-field `name` (FR-4.2) |
| `note` | string | Why this example is interesting (FR-4.3) |

```json
{
  "id": 12,
  "label": "Failure table fires",
  "inputs": { "text": "ABABDABACDABABCABAB", "pattern": "ABABCABAB" },
  "note": "Forces several non-trivial jumps using the failure function."
}
```

```ts
interface Example {
  id: number;
  label: string;
  inputs: Record<string, string | number | boolean>;
  note: string;
}
```

### 1.4 RunResult (the response of an execution)

| Field | Type | Notes |
|---|---|---|
| `runId` | integer | Identifier of the recorded run (FR-6.1) |
| `operation` | string | Operation slug |
| `result` | object | Operation-specific result; always contains a primary answer (see §9) |
| `explanation` | string | Plain-language account of *this* run (FR-3.3) |
| `complexity` | Complexity | Echoed for display |
| `visualizationLevel` | enum | Tells the frontend how to render |
| `trace` | Trace \| null | Ordered steps for `step_log`/`full`; `null` for `result`-level ops (FR-3.4) |
| `createdAt` | string | ISO timestamp |

```ts
interface RunResult {
  runId: number;
  operation: string;
  result: Record<string, unknown>;
  explanation: string;
  complexity: Complexity;
  visualizationLevel: VisualizationLevel;
  trace: Trace | null;
  createdAt: string;
}
```

### 1.5 ApiError

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "One or more inputs are invalid.",
    "details": [
      { "field": "shift", "issue": "OUT_OF_RANGE", "message": "Shift must be between 0 and 25." }
    ]
  }
}
```

```ts
interface FieldIssue { field: string; issue: string; message: string; }
interface ApiError { error: { code: string; message: string; details?: FieldIssue[] }; }
```

---

## 2. The `inputSpec` Format (FR-1.4, FR-2)

`inputSpec` describes the input panel for an operation so a **single** generic React form can render all twelve. It is stored as JSONB on `operations.input_spec`.

```ts
type FieldType = "string" | "integer" | "select" | "boolean";

interface InputField {
  name: string;            // key used in the run request `inputs` object
  label: string;           // shown to the user
  type: FieldType;
  required: boolean;
  placeholder?: string;
  default?: string | number | boolean;
  constraints?: {
    maxLength?: number;        // string
    minLength?: number;        // string
    allowedAlphabet?: string;  // string: regex-style class or explicit set, e.g. "A-Za-z"
    min?: number;              // integer
    max?: number;              // integer
    options?: { value: string; label: string }[];  // select
  };
}

interface InputSpec {
  fields: InputField[];
}
```

**Single-string operation** (e.g. `palindrome_check`):

```json
{ "fields": [
  { "name": "text", "label": "Text", "type": "string", "required": true,
    "placeholder": "Enter a string…", "constraints": { "maxLength": 200 } }
] }
```

**Two-string operation** (e.g. `edit_distance`, `kmp_search`):

```json
{ "fields": [
  { "name": "source", "label": "Source", "type": "string", "required": true, "constraints": { "maxLength": 60 } },
  { "name": "target", "label": "Target", "type": "string", "required": true, "constraints": { "maxLength": 60 } }
] }
```

**Mixed types** (e.g. `caesar_cipher` — string + integer + mode select):

```json
{ "fields": [
  { "name": "text",  "label": "Text",  "type": "string",  "required": true,
    "constraints": { "maxLength": 200, "allowedAlphabet": "A-Za-z " } },
  { "name": "shift", "label": "Shift", "type": "integer", "required": true, "default": 3,
    "constraints": { "min": 0, "max": 25 } },
  { "name": "mode",  "label": "Mode",  "type": "select",  "required": true, "default": "encode",
    "constraints": { "options": [ { "value": "encode", "label": "Encode" }, { "value": "decode", "label": "Decode" } ] } }
] }
```

> The frontend reads `inputSpec.fields` to render fields, applies `constraints` for client-side validation (FR-2.4), and builds the run request's `inputs` object keyed by each field's `name`.

---

## 3. The Trace & Step Schema (the heart — FR-3.4, FR-5)

The trace is the contract that lets the frontend animate **without understanding any algorithm**. It renders a list of `TraceStep` objects; the visualiser is a pure function of `(steps, currentStep)`.

```ts
interface Trace {
  steps: TraceStep[];
  meta: {
    totalSteps: number;
    family: "sequence" | "search" | "matrix";  // selects the visualiser
    axes?: { rowLabel?: string; colLabel?: string }; // matrix: the two strings
    dimensions?: { rows: number; cols: number };     // matrix
  };
}

interface TraceStep {
  index: number;          // 0-based, sequential
  action: TraceAction;    // see enum below
  message: string;        // human narration for the step log (FR-5.3)
  state?: SearchState | MatrixState | SequenceState; // snapshot at this step
  highlights?: Highlight[]; // what to colour, and why
}

type TraceAction =
  | "init" | "done"                                   // generic
  | "compare" | "match" | "mismatch" | "expand"       // sequence
  | "shift" | "jump" | "found"                         // search (with compare/match/mismatch)
  | "fill_cell" | "choose" | "trace_back";            // matrix

interface Highlight {
  target: "text" | "pattern" | "cell";
  index?: number;                 // single position (text/pattern)
  range?: [number, number];       // inclusive span (text/pattern)
  cell?: { row: number; col: number }; // matrix
  role: "active" | "compare" | "match" | "mismatch" | "path" | "result";
}
```

`role` carries *meaning*; the frontend maps each role to a Tailwind colour (e.g. `match` → green, `mismatch` → red, `path` → amber). Backend never sends colours.

**State variants:**

```ts
interface SequenceState { left: number; right: number; window?: [number, number]; }
interface SearchState {
  textIndex: number; patternIndex: number; shift: number;
  comparisons: number; failureTable?: number[];
}
interface MatrixState {
  cell: { row: number; col: number };
  value: number;
  choice?: "match" | "insert" | "delete" | "substitute";
}
```

### 3.1 Worked example — KMP (`family: "search"`)

Text `ABABCABAB`, pattern `ABAB` (abbreviated):

```json
{
  "meta": { "totalSteps": 9, "family": "search" },
  "steps": [
    { "index": 0, "action": "init",
      "message": "Failure table for \"ABAB\" computed as [0,0,1,2].",
      "state": { "textIndex": 0, "patternIndex": 0, "shift": 0, "comparisons": 0, "failureTable": [0,0,1,2] } },
    { "index": 1, "action": "compare", "message": "Compare text[0]=A with pattern[0]=A.",
      "state": { "textIndex": 0, "patternIndex": 0, "shift": 0, "comparisons": 1 },
      "highlights": [ { "target": "text", "index": 0, "role": "compare" }, { "target": "pattern", "index": 0, "role": "compare" } ] },
    { "index": 2, "action": "match", "message": "Match — advance both.",
      "highlights": [ { "target": "text", "index": 0, "role": "match" }, { "target": "pattern", "index": 0, "role": "match" } ] },
    { "index": 5, "action": "mismatch", "message": "text[4]=C ≠ pattern[4]. Use failure table to jump.",
      "state": { "textIndex": 4, "patternIndex": 4, "shift": 0, "comparisons": 5 },
      "highlights": [ { "target": "text", "index": 4, "role": "mismatch" } ] },
    { "index": 6, "action": "jump", "message": "Pattern index falls back to 2; text index stays at 4.",
      "state": { "textIndex": 4, "patternIndex": 2, "shift": 2, "comparisons": 5 } },
    { "index": 8, "action": "found", "message": "Full match ending at text index 8. Occurrence at position 5.",
      "highlights": [ { "target": "text", "range": [5, 8], "role": "result" } ] }
  ]
}
```

### 3.2 Worked example — Edit distance (`family: "matrix"`)

Source `kitten`, target `sitting` (abbreviated):

```json
{
  "meta": { "totalSteps": 56, "family": "matrix",
            "axes": { "rowLabel": "kitten", "colLabel": "sitting" },
            "dimensions": { "rows": 7, "cols": 8 } },
  "steps": [
    { "index": 0, "action": "init", "message": "Initialise first row and column with 0..n.",
      "highlights": [ { "target": "cell", "cell": { "row": 0, "col": 0 }, "role": "active" } ] },
    { "index": 9, "action": "fill_cell", "message": "Cell (1,1): k≠s → 1 + min(0,1,1) = 1.",
      "state": { "cell": { "row": 1, "col": 1 }, "value": 1, "choice": "substitute" },
      "highlights": [ { "target": "cell", "cell": { "row": 1, "col": 1 }, "role": "active" } ] },
    { "index": 55, "action": "trace_back", "message": "Optimal path traced: 3 edits (substitute, substitute, insert).",
      "highlights": [
        { "target": "cell", "cell": { "row": 1, "col": 1 }, "role": "path" },
        { "target": "cell", "cell": { "row": 6, "col": 7 }, "role": "path" }
      ] }
  ]
}
```

---

## 4. API Endpoints

All under `/api/v1`. Requests/responses are JSON. The session cookie is read/issued on every endpoint (§7).

### 4.1 `GET /catalog` — categories with operations
*Satisfies FR-1.1, FR-1.2, FR-1.3, FR-1.4.* Powers the home screen and the operation menu. Cacheable (catalogue is static).

**Request:** no body. **Response `200`:**

```json
{
  "categories": [
    {
      "slug": "search", "name": "Search & Matching",
      "description": "Locate a pattern within a text…", "displayOrder": 2,
      "operations": [
        { "slug": "kmp_search", "name": "Knuth–Morris–Pratt Search", "categorySlug": "search",
          "description": "Find every position…", "explanation": "KMP precomputes…",
          "complexity": { "time": "O(n+m)", "space": "O(m)" },
          "visualizationLevel": "full", "inputSpec": { "fields": [ /* … */ ] } }
      ]
    }
  ]
}
```

### 4.2 `GET /operations/{slug}` — operation detail + examples
*Satisfies FR-1.3, FR-1.4, FR-4.1, FR-4.3.* Returns the full operation plus its examples.

**Path param:** `slug` (string). **Response `200`:**

```json
{
  "operation": { "slug": "kmp_search", "name": "Knuth–Morris–Pratt Search", "categorySlug": "search",
    "description": "…", "explanation": "…", "complexity": { "time": "O(n+m)", "space": "O(m)" },
    "visualizationLevel": "full", "inputSpec": { "fields": [ /* … */ ] } },
  "examples": [
    { "id": 12, "label": "Failure table fires",
      "inputs": { "text": "ABABDABACDABABCABAB", "pattern": "ABABCABAB" },
      "note": "Forces several non-trivial jumps." }
  ]
}
```

**Errors:** `404 OPERATION_NOT_FOUND` if `slug` is unknown.

### 4.3 `POST /operations/{slug}/validate` — server-side validation (optional)
*Satisfies FR-2.2, FR-2.3.* Lets the frontend confirm inputs without executing. (Validation also runs client-side from `inputSpec`, and again inside `run`.)

**Request:**

```json
{ "inputs": { "text": "Hello", "shift": 30, "mode": "encode" } }
```

**Response `200` (valid):** `{ "valid": true }`
**Response `422` (invalid):**

```json
{ "error": { "code": "VALIDATION_ERROR", "message": "One or more inputs are invalid.",
  "details": [ { "field": "shift", "issue": "OUT_OF_RANGE", "message": "Shift must be between 0 and 25." } ] } }
```

### 4.4 `POST /operations/{slug}/run` — execute the operation ★
*Satisfies FR-2, FR-3.1–3.5, FR-5 (trace), FR-6.1, FR-6.2, FR-7.2.* The core endpoint. Validates, runs the Python function, builds the trace, records the run, and (if missing) issues the session cookie.

**Path param:** `slug`. **Request:**

```json
{ "inputs": { "text": "ABABCABAB", "pattern": "ABAB" } }
```

**Response `200`:** a `RunResult` (see §1.4):

```json
{
  "runId": 1432,
  "operation": "kmp_search",
  "result": { "positions": [5], "count": 1, "comparisons": 11 },
  "explanation": "Found 1 occurrence at position 5 using 11 character comparisons; the failure table avoided re-scanning.",
  "complexity": { "time": "O(n+m)", "space": "O(m)" },
  "visualizationLevel": "full",
  "trace": { "meta": { "totalSteps": 9, "family": "search" }, "steps": [ /* §3.1 */ ] },
  "createdAt": "2026-06-12T09:30:00Z"
}
```

For a `result`-level operation, `trace` is `null`:

```json
{ "runId": 1433, "operation": "palindrome_check",
  "result": { "isPalindrome": true },
  "explanation": "\"level\" reads the same forwards and backwards.",
  "complexity": { "time": "O(n)", "space": "O(1)" },
  "visualizationLevel": "result", "trace": null, "createdAt": "2026-06-12T09:31:00Z" }
```

**Errors:** `404 OPERATION_NOT_FOUND`; `422 VALIDATION_ERROR` (with `details`).

### 4.5 `GET /runs` — recent runs for this session
*Satisfies FR-6.3, FR-6.4.* Scoped to the caller's `sl_session` cookie. Paginated.

**Query params:** `limit` (default 20, max 100), `offset` (default 0), optional `operation` (filter by slug).

**Response `200`:**

```json
{
  "runs": [
    { "runId": 1432, "operation": "kmp_search",
      "inputs": { "text": "ABABCABAB", "pattern": "ABAB" },
      "resultSummary": "1 occurrence at position 5", "createdAt": "2026-06-12T09:30:00Z" }
  ],
  "meta": { "limit": 20, "offset": 0, "total": 37 }
}
```

> List items carry a short `resultSummary` rather than the full result/trace to keep the payload light; fetch a full run via §4.6.

### 4.6 `GET /runs/{runId}` — a single run (with cached trace)
*Satisfies FR-6.2.* Returns the stored run, including the cached trace if one was saved — so a replay needs no recomputation. Only returns runs belonging to the caller's session.

**Response `200`:** a full `RunResult` (§1.4).
**Errors:** `404 RUN_NOT_FOUND` (also returned if the run belongs to another session, to avoid leaking existence).

### 4.7 `GET /session` — current session (convenience)
*Satisfies FR-7.2.* Ensures a session cookie exists and reports lightweight info. Useful for the frontend to display a "your recent runs" affordance.

**Response `200`:** `{ "sessionStarted": "2026-06-12T09:00:00Z", "runCount": 37 }`
(Sets the `sl_session` cookie on the response if it was absent.)

### 4.8 `GET /health` — liveness
Ops nicety. **Response `200`:** `{ "status": "ok", "version": "1.0.0" }`

---

## 5. Error Model

Every error response uses the `ApiError` envelope (§1.5). HTTP status codes:

| Status | When | `error.code` examples |
|---|---|---|
| `200` | Success | — |
| `404` | Unknown operation slug or run id | `OPERATION_NOT_FOUND`, `RUN_NOT_FOUND` |
| `422` | Input validation failed | `VALIDATION_ERROR` (with `details[]`) |
| `429` | Rate limit exceeded (optional, §10) | `RATE_LIMITED` |
| `500` | Unexpected server error | `INTERNAL_ERROR` |

**Validation `issue` vocabulary** (machine-readable, in `details[].issue`):
`REQUIRED` · `TOO_LONG` · `TOO_SHORT` · `OUT_OF_RANGE` · `INVALID_ALPHABET` · `INVALID_OPTION` · `NOT_AN_INTEGER`.

---

## 6. Validation Rules (FR-2.3)

Validation runs in three places against the same `inputSpec`: in the browser before sending (UX), and in the backend on `validate` and `run` (authority). Each `InputField.constraints` maps to an `issue`:

| Constraint | Applies to | Violated → issue |
|---|---|---|
| `required` | all | `REQUIRED` |
| `maxLength` / `minLength` | string | `TOO_LONG` / `TOO_SHORT` |
| `allowedAlphabet` | string | `INVALID_ALPHABET` |
| `min` / `max` | integer | `OUT_OF_RANGE` |
| (parse) | integer | `NOT_AN_INTEGER` |
| `options` | select | `INVALID_OPTION` |

Agreed default behaviours: empty required input is rejected (`REQUIRED`); a pattern longer than the text in search operations is **valid** and simply yields zero occurrences; for the cipher, characters outside `allowedAlphabet` are rejected rather than silently passed through.

---

## 7. Session & Cookie Contract (FR-7.2, FR-7.3)

| Property | Value |
|---|---|
| Cookie name | `sl_session` |
| Value | Opaque server-generated UUID (no personal data) |
| Flags | `HttpOnly`, `SameSite=Lax`, `Secure` (production/HTTPS only), `Path=/` |
| Lifetime | `Max-Age` = 30 days |
| Issued | On the first request lacking the cookie; the backend sets it on the response |
| Used for | Scoping `runs` to a visitor (read server-side only) |

The frontend never reads or sets this cookie (it is `HttpOnly`). For cross-origin dev (Vite dev server → FastAPI), the frontend must send requests with credentials included, and the backend CORS config must allow credentials and name the exact frontend origin (a wildcard origin is not allowed with credentials). No login, registration, or personal data is ever requested (FR-7.3); there is no `users` table.

---

## 8. Persistence Mapping (API ↔ PostgreSQL via SQLAlchemy)

API objects (camelCase) map to tables (snake_case). JSONB columns hold the variable-shape data.

| Table | Key columns (snake_case) | JSONB columns | Serves API object |
|---|---|---|---|
| `categories` | `category_id`, `slug`, `name`, `description`, `display_order` | — | Category |
| `operations` | `operation_id`, `slug`, `name`, `category_id`→, `description`, `explanation`, `time_complexity`, `space_complexity`, `visualisation_level` | `input_spec` | Operation |
| `examples` | `example_id`, `operation_id`→, `label`, `note`, `display_order` | `inputs` | Example |
| `runs` | `run_id`, `operation_id`→, `session_id`, `created_at` | `input_values`, `result`, `trace` | RunResult |

Mapping notes: `operations.time_complexity` + `space_complexity` compose the API's `complexity` object; `operations.visualisation_level` becomes `visualizationLevel`; `runs.trace` is nullable and only populated for `step_log`/`full` operations (FR-6.2); `runs.session_id` is the `sl_session` value, never exposed in responses.

---

## 9. The Twelve Operations — Concrete Specs

`viz` = visualizationLevel. `inputs` lists field `name`s (types in parentheses).

| # | slug | category | inputs | viz | `result` keys |
|---|---|---|---|---|---|
| 1 | `palindrome_check` | analysis | `text`(string) | result | `isPalindrome`(bool) |
| 2 | `char_frequency` | analysis | `text`(string) | result | `counts`(obj), `total`, `distinct` |
| 3 | `longest_palindrome` | analysis | `text`(string) | step_log | `substring`, `start`, `length` |
| 4 | `find_all_occurrences` | search | `text`, `pattern` | result | `positions`(int[]), `count` |
| 5 | `count_occurrences` | search | `text`, `pattern` | result | `count` |
| 6 | `kmp_search` | search | `text`, `pattern` | **full** | `positions`, `count`, `comparisons` |
| 7 | `anagram_check` | comparison | `source`, `target` | result | `areAnagrams`(bool) |
| 8 | `edit_distance` | comparison | `source`, `target` | **full** | `distance`, `operations`(obj[]) |
| 9 | `lcs` | comparison | `source`, `target` | step_log | `length`, `subsequence` |
| 10 | `reverse_transform` | transform | `text`, `mode`(select: reverse/upper/lower/title/swapcase) | result | `output` |
| 11 | `caesar_cipher` | transform | `text`, `shift`(int 0–25), `mode`(select: encode/decode) | result | `output`, `shiftUsed` |
| 12 | `run_length` | transform | `text`, `mode`(select: encode/decode) | result | `output`, `ratio` |

**Sample requests/results:**

```json
// edit_distance
→ { "inputs": { "source": "kitten", "target": "sitting" } }
← result: { "distance": 3, "operations": [
     { "type": "substitute", "at": 0, "from": "k", "to": "s" },
     { "type": "substitute", "at": 4, "from": "e", "to": "i" },
     { "type": "insert", "at": 6, "char": "g" } ] }

// char_frequency
→ { "inputs": { "text": "banana" } }
← result: { "counts": { "b": 1, "a": 3, "n": 2 }, "total": 6, "distinct": 3 }

// caesar_cipher
→ { "inputs": { "text": "Hello", "shift": 3, "mode": "encode" } }
← result: { "output": "Khoor", "shiftUsed": 3 }

// run_length
→ { "inputs": { "text": "aaabbc", "mode": "encode" } }
← result: { "output": "a3b2c1", "ratio": 0.67 }
```

---

## 10. Recommended Extensions (optional — build only if time allows)

These stay within the FR context and add polish without new scope risk:

- **Pagination meta** on `/runs` (already specified) — keeps the history view fast as runs accumulate.
- **`requestId`** echoed in every response header (`X-Request-Id`) — trivial to add, makes debugging during the demo far easier.
- **Caching headers** (`Cache-Control`, `ETag`) on `/catalog` and `/operations/{slug}` — the catalogue is static, so the frontend can cache it.
- **Lightweight rate limit** on `/run` (e.g. per session) returning `429 RATE_LIMITED` — guards the live demo against accidental floods.
- **`sessions` table** (per §8 of the report) — only if you want session analytics; otherwise `runs.session_id` suffices.

---

## 11. Locked Decisions Recap

1. API JSON is **camelCase**; DB is **snake_case**; SQLAlchemy/Pydantic map between them.
2. Operations are addressed by **`slug`**; runs by integer **`runId`**.
3. The **trace `family`** (`sequence` | `search` | `matrix`) selects the visualiser; `role` selects the colour.
4. The **`run` endpoint** is the single execution path: validate → compute → trace → record → respond.
5. Identity is an **anonymous `sl_session` HttpOnly cookie**; no users, no personal data.
6. `trace` is **`null`** for `result`-level operations and present for `step_log`/`full`.
7. Two flagship operations (`kmp_search`, `edit_distance`) ship the **full** animation; the rest follow this same contract at a lighter visualisation level.
