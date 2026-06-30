# Snippet Extensions Reference

Snippets are **data-only** (no Rust). An extension ships one or more JSON files of snippets, referenced from the manifest. Snippets are backed by the `simple-completion-language-server` under the hood, but as an author you just write JSON.

## Manifest

```toml
snippets = ["./snippets/rust.json", "./snippets/typescript.json"]
```

An array of paths relative to `extension.toml`. **Scope is decided by the file name** (lowercase language name):

- `rust.json` → applies in Rust buffers.
- `python.json` → Python; `shell script.json` → Shell Script (note the space — it's the lowercase language *name*, not the file extension).
- `snippets.json` → applies in **all** languages regardless of buffer.

Naming exceptions worth knowing:

- JSX snippets go in `javascript.json` (not `jsx.json`).
- TSX and TypeScript follow the normal rule (`tsx.json`, `typescript.json`).

Convention: a snippets-only extension's `id` should end in `-snippets`.

## Snippet file format

A JSON object whose keys are snippet **names** and whose values are snippet definitions:

```json
{
  "Log to console": {
    "prefix": "log",
    "body": ["console.info(\"Hello, ${1:World}!\")", "$0"],
    "description": "Logs to console"
  },
  "Function": {
    "prefix": ["fn", "func"],
    "body": [
      "function ${1:name}(${2:args}) {",
      "\t$0",
      "}"
    ],
    "description": "Function declaration"
  }
}
```

Fields:

- **name** (the object key) — required. Used as the trigger if `prefix` is omitted.
- **`prefix`** — optional; the text that triggers the snippet. A string, or an array of strings (only the first is currently used). If omitted, the name triggers it. (Prefixes generally shouldn't contain characters that break word-boundary matching — e.g. a leading/embedded `-` can prevent triggering; prefer `vsetup` over `v-setup`.)
- **`body`** — required. The inserted text. A string, or an array of strings (one per line — clearer for multi-line). Use `\t` for indentation.
- **`description`** — optional; shown in the completion menu.

### Placeholders (LSP snippet syntax)

- `$1`, `$2`, … — tab stops, visited in order.
- `${1:default}` — tab stop with default text.
- `$0` — final cursor position after the last tab stop.
- Identical placeholder numbers are **linked** — editing one edits all.
- A literal `$` outside a placeholder must be escaped as `\\$` in the JSON string (e.g. `"\\$var"`).

## Directory layout

```
my-snippets/
  extension.toml
  LICENSE
  snippets/
    rust.json
    typescript.json
    snippets.json        # global snippets (optional)
```

## Testing

Install as a dev extension, open a buffer of the target language, type a prefix, and confirm the snippet appears and tab stops work. Note: Zed may create a per-scope file (e.g. `vue.js.json`) when you configure snippets via the command palette — when developing an *extension*, keep your snippets in the extension's `snippets/` dir and reference them in the manifest. User-level snippets (separate from extensions) live in `~/.config/zed/snippets/`. See `references/publishing.md`.
