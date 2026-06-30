# Theme & Icon Theme Extensions Reference

Both are **data-only** (no Rust). A theme is a JSON "theme family" containing one or more variants. The hard rule: **themes and icon themes must be published as their own extension** — they cannot be bundled with language support or each other in a published extension, even if developed in the same repo.

The fastest way to author a color theme is Zed's visual **Theme Builder** (<https://zed.dev/theme-builder>): edit with live preview, right-click any UI element to find the token controlling it, then export the JSON or a full extension. For hand-editing, point your editor at the published schema for completion + validation.

---

## Part 1 — Color Themes

### Manifest

```toml
themes = ["themes/my-theme.json"]
```
Array of paths (relative to `extension.toml`) to theme-family files.

### File structure (schema v0.2.0)

```json
{
  "$schema": "https://zed.dev/schema/themes/v0.2.0.json",
  "name": "My Theme",
  "author": "Your Name",
  "themes": [
    {
      "name": "My Theme Dark",
      "appearance": "dark",
      "style": {
        "background": "#1e1e1e",
        "foreground": "#d4d4d4",
        "editor.background": "#1e1e1e",
        "editor.foreground": "#d4d4d4",
        "...": "...",
        "players": [ /* see below */ ],
        "syntax": { /* see below */ }
      }
    },
    {
      "name": "My Theme Light",
      "appearance": "light",
      "style": { "...": "..." }
    }
  ]
}
```

- `name` / `author` — family-level identity.
- `themes[]` — each variant is selectable independently in the theme picker.
- `appearance` — `"dark"` or `"light"`. Drives which variant pairs with light/dark mode and which base defaults Zed fills in for unset keys.
- `style` — the styled surface. Any key you omit inherits from Zed's base (light or dark) defaults, so you only need to set what you want to change.

### The `style` object

There are **200+ UI style keys** plus the `syntax` and `players` sub-objects. Rather than memorize them, rely on the schema (`https://zed.dev/schema/themes/v0.2.0.json`) for the authoritative, complete list, and crib from a built-in theme (`assets/themes/one/one.json` in `zed-industries/zed`). The keys are grouped roughly as:

- **Base:** `background`, `foreground`, `accent`, `border`, `border.variant`, `border.focused`, `border.selected`, `border.disabled`, `border.transparent`.
- **Surfaces:** `elevated_surface.background`, `surface.background`, `element.{background,hover,active,selected,disabled}`, `ghost_element.{...}`, `drop_target.background`.
- **Text & icons:** `text`, `text.muted`, `text.placeholder`, `text.disabled`, `text.accent`; `icon`, `icon.muted`, `icon.disabled`, `icon.placeholder`, `icon.accent`.
- **Chrome:** `status_bar.background`, `title_bar.background`, `toolbar.background`, `tab_bar.background`, `tab.{active,inactive}_background`, `panel.background`, `panel.focused_border`, `scrollbar.*`.
- **Editor:** `editor.background`, `editor.foreground`, `editor.gutter.background`, `editor.line_number`, `editor.active_line.background`, `editor.active_line_number`, `editor.highlighted_line.background`, `editor.wrap_guide`, `editor.document_highlight.{read,write}_background`, `editor.indent_guide`, `editor.indent_guide_active`.
- **Diff/VCS:** `created`, `modified`, `deleted`, `conflict`, `hint`, `predictive`; the `*.background`/`*.border` variants.
- **Diagnostics:** `error`, `warning`, `info`, `success`, and their `*.background`/`*.border` forms.
- **Terminal:** `terminal.background`, `terminal.foreground`, `terminal.ansi.{black,red,green,yellow,blue,magenta,cyan,white}` and their `bright_*` variants.

Values are hex colors. Many accept 8-digit hex (`#rrggbbaa`) for alpha (e.g. translucent selection backgrounds).

### `players` (collaboration cursors)

An array (typically 8 entries) defining per-participant colors for multiplayer:

```json
"players": [
  { "cursor": "#569cd6", "background": "#569cd6", "selection": "#569cd633" },
  { "cursor": "#4ec9b0", "background": "#4ec9b0", "selection": "#4ec9b033" }
]
```
Each entry: `cursor`, `background` (avatar/cursor label), `selection` (their selection highlight, usually the cursor color at low alpha).

### `syntax` (highlighting)

Maps highlight capture names (the `@...` names from `highlights.scm`, written **without** the `@`) to a style:

```json
"syntax": {
  "comment":         { "color": "#6a9955", "font_style": "italic" },
  "comment.doc":     { "color": "#6a9955", "font_style": "italic" },
  "keyword":         { "color": "#569cd6" },
  "string":          { "color": "#ce9178" },
  "string.escape":   { "color": "#d7ba7d" },
  "function":        { "color": "#dcdcaa" },
  "type":            { "color": "#4ec9b0" },
  "type.builtin":    { "color": "#4ec9b0" },
  "constant":        { "color": "#4fc1ff" },
  "number":          { "color": "#b5cea8" },
  "operator":        { "color": "#d4d4d4" },
  "variable":        { "color": "#9cdcfe" },
  "variable.parameter": { "color": "#9cdcfe" },
  "punctuation":     { "color": "#d4d4d4" },
  "tag":             { "color": "#569cd6" },
  "attribute":       { "color": "#9cdcfe" }
}
```
Per-key style fields: `color`, `font_style` (`"normal"`/`"italic"`), `font_weight` (100–900). The complete set of syntax keys mirrors the capture list in `references/languages.md` (§3.1) — define styles for the captures your target languages emit; undefined captures fall back per the right-to-left fallback rule.

### Tips
- Set `appearance` correctly — it controls the base defaults Zed merges in, so a "dark" theme with light values will look wrong on unset keys.
- You don't have to set every key; start from a built-in theme's JSON and adjust.
- Test by installing as a dev extension and toggling with the theme selector (`cmd-k cmd-t` / `ctrl-k ctrl-t`), which previews live as you navigate.

---

## Part 2 — Icon Themes

### Manifest

```toml
icon_themes = ["icon_themes/my-icon-theme.json"]
```
Plus the SVG assets the JSON references (commonly under `icon_themes/icons/`).

### File structure (schema v0.3.0)

```json
{
  "$schema": "https://zed.dev/schema/icon_themes/v0.3.0.json",
  "name": "My Icon Theme",
  "author": "Your Name",
  "themes": [
    {
      "name": "My Icon Theme",
      "appearance": "dark",
      "directory_icons": {
        "collapsed": "./icons/folder.svg",
        "expanded": "./icons/folder-open.svg"
      },
      "named_directory_icons": {
        "stylesheets": {
          "collapsed": "./icons/folder-stylesheets.svg",
          "expanded": "./icons/folder-stylesheets-open.svg"
        }
      },
      "chevron_icons": {
        "collapsed": "./icons/chevron-right.svg",
        "expanded": "./icons/chevron-down.svg"
      },
      "file_stems": { "Makefile": "make" },
      "file_suffixes": { "mp3": "audio", "rs": "rust", "ts": "typescript" },
      "file_icons": {
        "default": { "path": "./icons/file.svg" },
        "audio":   { "path": "./icons/audio.svg" },
        "make":    { "path": "./icons/make.svg" },
        "rust":    { "path": "./icons/rust.svg" },
        "typescript": { "path": "./icons/typescript.svg" }
      }
    }
  ]
}
```

How resolution works:
- **`directory_icons`** — default collapsed/expanded folder icons.
- **`named_directory_icons`** — per-folder-name overrides (keyed by a logical name that ties into how Zed matches directory names).
- **`chevron_icons`** — the expand/collapse chevrons in the project panel.
- **`file_suffixes`** — maps a file extension (e.g. `"rs"`) to an **icon key**.
- **`file_stems`** — maps a full filename stem (e.g. `"Makefile"`) to an icon key.
- **`file_icons`** — maps each **icon key** to an SVG `{ "path": ... }`. Must include a `"default"` used when nothing else matches.

So a `.rs` file resolves: `file_suffixes["rs"]` → `"rust"` → `file_icons["rust"].path`. Paths are resolved **relative to the extension root**.

`appearance` works as for color themes; you can ship separate light/dark icon variants in the `themes` array.

### SVG guidelines
- Use `fill="currentColor"` (or `stroke="currentColor"`) so icons inherit the UI color and adapt to light/dark:
  ```svg
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">
    <path fill="currentColor" d="M8 1l7 4v6l-7 4-7-4V5l7-4z"/>
  </svg>
  ```
- Keep a consistent `viewBox` (16×16 is typical) and optimize the SVGs (strip editor metadata) so the extension stays lean.
- Ship only the icons you actually reference.

---

## Publishing (both)
Theme and icon-theme extensions follow the standard flow in `references/publishing.md`: a repo with `extension.toml` + the JSON (+ SVGs), a license, a submodule PR to `zed-industries/extensions`. Remember the id convention (`-theme` / `-icon-theme`) and that they must be standalone extensions. Third-party gallery for color-theme inspiration with live previews: <https://zed-themes.com>.
