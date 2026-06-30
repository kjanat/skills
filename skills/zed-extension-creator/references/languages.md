# Language Extensions Reference

Adding a language to Zed has up to four parts: **metadata** (`config.toml`), a **grammar** (tree-sitter, registered in `extension.toml`), **queries** (`.scm` files that tell Zed how to use the syntax tree), and optionally a **language server** (covered in `references/language-servers.md`). Highlighting, indentation, outline, brackets, etc. come purely from the grammar + queries — **no Rust needed**. The language server is a separate, optional Rust layer.

The single best source of real-world examples is Zed's own built-in languages: <https://github.com/zed-industries/zed/tree/main/crates/languages/src>. When unsure how to write a query, copy the pattern from a similar built-in language.

## 1. Metadata: `languages/<lang>/config.toml`

Each language lives in its own subdirectory under `languages/`. The directory name is arbitrary; the `name` field is what matters.

```toml
name = "My Language"              # required — shows in the language picker; LSP `languages` must match this
grammar = "my-language"          # required — the [grammars.X] key from extension.toml
path_suffixes = ["myl", "mylang"]  # file extensions (NOT globs; just suffixes)
line_comments = ["# "]           # used by editor::ToggleComments
tab_size = 4                     # default 4
hard_tabs = false                # tabs vs spaces; default false (spaces)
first_line_pattern = "^#!.*\\bmylang\\b"   # regex on first line (e.g. shebang detection)
# debuggers = ["my-debug-adapter"]         # order debuggers in the New Process modal
```

Field notes:
- `path_suffixes` are plain suffixes, **not** glob patterns (unlike the user-settings `file_types`). For glob matching, users add `file_types` in their settings.
- `first_line_pattern` matches files by their first line — used for scripts identified by shebang.
- `line_comments` powers comment toggling (`cmd-/`).
- Additional per-language settings (e.g. `word_characters`, `brackets`, `[overrides.*]`) also live here; see Overrides below.

## 2. Grammar registration: `extension.toml`

```toml
[grammars.my-language]
repository = "https://github.com/org/tree-sitter-my-language"
rev = "<commit-sha>"
# path = "subdir"   # if the grammar is in a repo subdirectory
```

- `rev` should be a commit SHA for reproducibility (a tag works too).
- `file://` URLs are allowed for **local** grammar development.
- The table key (`my-language`) is referenced by `grammar = "my-language"` in `config.toml`.
- If no suitable tree-sitter grammar exists, you can [write one](https://tree-sitter.github.io/tree-sitter/creating-parsers/3-writing-the-grammar.html); grammars are JS that the tree-sitter CLI compiles to C, which Zed compiles to wasm.

## 3. Tree-sitter queries (`.scm` files)

Queries live alongside `config.toml` in `languages/<lang>/`. They use the [tree-sitter query language](https://tree-sitter.github.io/tree-sitter/using-parsers/queries/). Each file name maps to a feature. Only `highlights.scm` is essential; add the rest as the language warrants.

| File | Feature |
|---|---|
| `highlights.scm` | Syntax highlighting |
| `injections.scm` | Embedding one language in another (code blocks, SQL-in-string) |
| `brackets.scm` | Bracket matching + rainbow brackets |
| `indents.scm` | Auto-indentation |
| `outline.scm` | Code outline / structure / breadcrumbs |
| `textobjects.scm` | Vim text-object & section navigation |
| `runnables.scm` | "Run" buttons for detected runnable code |
| `overrides.scm` | Scoped setting overrides (e.g. inside strings/comments) |
| `redactions.scm` | Hide values when screen-sharing |

### 3.1 `highlights.scm`

Capture syntax nodes and tag them with a highlight name the theme styles.

```scheme
(string) @string
(pair key: (string) @property)
(number) @number
(true) @boolean
(comment) @comment
```

**Full list of theme-recognized captures:**

`@attribute` · `@boolean` · `@comment` · `@comment.doc` · `@constant` · `@constant.builtin` · `@constructor` · `@embedded` · `@emphasis` · `@emphasis.strong` · `@enum` · `@function` · `@hint` · `@keyword` · `@label` · `@link_text` · `@link_uri` · `@number` · `@operator` · `@predictive` · `@preproc` · `@primary` · `@property` · `@punctuation` · `@punctuation.bracket` · `@punctuation.delimiter` · `@punctuation.list_marker` · `@punctuation.special` · `@string` · `@string.escape` · `@string.regex` · `@string.special` · `@string.special.symbol` · `@tag` · `@tag.doctype` · `@text.literal` · `@title` · `@type` · `@type.builtin` · `@variable` · `@variable.special` · `@variable.parameter` · `@variant`

**Fallback captures:** a node can carry multiple captures; Zed resolves **right-to-left**, using the first the theme defines.
```scheme
(type_identifier) @type @variable
; tries @variable first; if the theme has no style for it, falls back to @type
```
This lets you offer a preferred highlight while still rendering in themes that lack it.

### 3.2 `injections.scm`

Embed another language's grammar inside this one.

```scheme
(fenced_code_block
  (info_string (language) @injection.language)
  (code_fence_content) @injection.content)

((inline) @content
 (#set! injection.language "markdown-inline"))
```
- `@injection.language` — captures the embedded language identifier (dynamic), or set a fixed one with `(#set! injection.language "...")`.
- `@injection.content` — the text to reparse as the injected language.

### 3.3 `brackets.scm`

```scheme
("[" @open "]" @close)
("{" @open "}" @close)
("\"" @open "\"" @close)
```
`@open`/`@close` mark pairs. To exclude a pair from rainbow coloring:
```scheme
(("\"" @open "\"" @close) (#set! rainbow.exclude))
```

### 3.4 `indents.scm`

```scheme
(array "]" @end) @indent
(object "}" @end) @indent
```
`@indent` marks a node whose body should be indented; `@end` marks the closing token that dedents.

### 3.5 `outline.scm`

```scheme
(pair key: (string (string_content) @name)) @item
```
Captures: `@name` (the displayed label text), `@item` (the whole entry), `@context` / `@context.extra` (extra context shown with the item), `@annotation` (doc comments/attributes/decorators preceding the item — used by the agent when generating code edits).

### 3.6 `textobjects.scm` (Vim mode)

Defines function/class/comment objects for `af`/`if`/`ac`/`ic` and section motions. For languages without functions/classes, map analogous constructs (CSS: a rule-set = method, a media-query = class).

| Capture | Object / motions |
|---|---|
| `@function.around` | `af`; `[m` `]m` `[M` `]M` |
| `@function.inside` | `if` |
| `@class.around` | `ac`; `[[` `]]` `[]` `][` |
| `@class.inside` | `ic` |
| `@comment.around` | `gc` |
| `@comment.inside` | `igc` |

```scheme
(method_definition
  body: (_ "{" (_)* @function.inside "}")) @function.around
(function_signature_item) @function.around   ; declarations with no body
(comment)+ @comment.around                    ; join adjacent comments
```
Closures generally should *not* count as functions. `nvim-treesitter-textobjects` and Helix have queries for many languages to adapt.

### 3.7 `runnables.scm`

Detect runnable code and show a Run button.

```scheme
(
  (document (object (pair
    key: (string (string_content) @_name (#eq? @_name "scripts"))
    value: (object (pair key: (string (string_content) @run @script))))))
  (#set! tag package-script)
)
```
- `@run` — where the run button appears.
- Captures **not** prefixed with `_` are exported as env vars `ZED_CUSTOM_<NAME>` to the run command.
- `(#set! tag ...)` tags the runnable so a matching task template can pick it up.

### 3.8 `overrides.scm`

Define syntactic scopes used to override settings inside specific constructs. Pair with `[overrides.<scope>]` in `config.toml`.

```scheme
; overrides.scm
[ (string) (template_string) ] @string
(comment) @comment.inclusive       ; .inclusive extends the scope through the trailing newline
```
```toml
# config.toml
word_characters = ["#", "$"]

[overrides.string]
completion_query_characters = ["-"]
```
Ranges are **exclusive** by default (cursor must be strictly inside). Add the `.inclusive` suffix to a capture to make the scope inclusive (e.g. so a line comment's scope reaches the newline). You can also disable specific auto-closing brackets within a scope via `not_in` on the bracket definition in `config.toml`:
```toml
brackets = [
  { start = "'", end = "'", close = true, newline = false, not_in = ["string", "comment"] },
]
```

### 3.9 `redactions.scm`

Mark values to render redacted during screen-share.
```scheme
(pair value: (number) @redact)
(pair value: (string) @redact)
```

## 4. Language servers from a language extension

To also provide IDE features, declare the server in `extension.toml` and implement the Rust side. The `languages` array must list `name`s matching your `config.toml`:

```toml
[language_servers.my-language-lsp]
name = "My Language LSP"
languages = ["My Language"]
```

Implementation patterns (downloading the server, caching, completion labels, init/workspace config, multi-language `language_ids`) are in `references/language-servers.md`.

## 5. Semantic tokens (optional, LSP-driven highlighting)

If your language server emits semantic tokens, you can ship default style rules for its custom token types. Place `semantic_token_rules.json` next to `config.toml`:

```json
[
  { "token_type": "lifetime",   "style": ["lifetime"] },
  { "token_type": "builtinType","style": ["type"] },
  { "token_type": "selfKeyword","style": ["variable.special"] }
]
```
Same format as the user `semantic_token_rules` setting. Precedence: user settings > extension rules > Zed built-in defaults. Users enable semantic tokens with `"semantic_tokens": "combined"` (tree-sitter + LSP) or `"full"` (LSP only); default is `"off"`. Each rule supports `token_type`, `token_modifiers`, `style`, `foreground_color`, `background_color`, `underline`, `strikethrough`, `font_weight`, `font_style`.
