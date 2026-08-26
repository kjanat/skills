# Distribution, registry metadata, and npm

Read this when publishing a plugin, adding it to the registry, or deciding whether to ship an npm
package. Keep these four surfaces distinct:

1. **Registry name** — `dprint add <USER>/<short>` is the stable user-facing command.
2. **GitHub release** — owns immutable `plugin.wasm` or `plugin.json` assets used by the proxy.
3. **npm package** — a first-class source for the dprint CLI for both Wasm and process plugins.
4. **`@dprint/formatter`** — a programmatic Wasm host; it does not run process plugins.

The npm distinction changed in [dprint/dprint#1183] and [dprint/dprint#1215]. Do not repeat the old rule
that process plugins cannot be distributed on npm: npm can carry their `plugin.json` for CLI installation,
but they still cannot execute through `@dprint/formatter`.

Compatibility floor: npm specifiers, smart init metadata, overrides, and additive associations shipped in
[dprint 0.55.0]; automatic preference for registry-declared npm packages shipped in [dprint 0.56.0]. If
supporting older CLIs, keep the documented install path and config examples within their feature set.

[dprint/dprint#1183]: https://github.com/dprint/dprint/pull/1183
[dprint/dprint#1215]: https://github.com/dprint/dprint/pull/1215
[dprint 0.55.0]: https://github.com/dprint/dprint/releases/tag/0.55.0
[dprint 0.56.0]: https://github.com/dprint/dprint/releases/tag/0.56.0

## Registry metadata

Keep the registry entry and the plugin's `latest.json` aligned with the release:

- The registry `info.json` entry carries `name`, `version`, `url`, `configKey`, `fileExtensions`,
  `fileNames`, `configExcludes`, and an optional `checksum`.
- The plugin's `latest.json` carries `version`, `url`, and an optional `checksum` for update resolution.
- Either file may declare `npm: { "name": "<package>" }`; add `path` when the plugin is not at the
  package root. Keep both declarations identical when both are present.
- In `info.json`, `defaultConfig` is an object inserted into the selected plugin's config block by
  `dprint init`.
- Also in `info.json`, `configItems` contains `{ match, config }` fragments. Each `match` may declare
  `fileExtensions` or `fileNames`; matching fragments are deep-merged, with arrays concatenated.

`dprint init` uses the file metadata and `configItems` to pre-select plugins. Registry order wins when
plugins compete for the same extension or config key, so use a distinct, stable config key and declare
only files the plugin genuinely handles. See [#1185], [#1186], and [#1187].

[#1185]: https://github.com/dprint/dprint/pull/1185
[#1186]: https://github.com/dprint/dprint/pull/1186
[#1187]: https://github.com/dprint/dprint/pull/1187

When `npm` is declared, dprint resolves the version from npm's `dist-tags.latest`, not the possibly stale
version in `info.json` or `latest.json`. Publish the npm version before advertising it in registry
metadata. A malformed or unreachable npm declaration falls back differently by command, so test `init`,
`add`, and `config update` rather than assuming one happy path.

## npm package layouts

### Wasm plugin

Bundle the Wasm and make its path unambiguous:

```text
npm:@scope/plugin@1.2.3
npm:@scope/plugin@1.2.3/plugin.wasm
npm:@scope/plugin@1.2.3/subdir/plugin.wasm
```

The root form defaults to `plugin.wasm`; registry metadata may declare another `path`. If the package is
also intended for programmatic use, export `getPath()` or `getBuffer()` so callers can pass the bytes to
`@dprint/formatter`. Keep the npm version, git tag, plugin version, and schema `$id` in lockstep.

### Process plugin

Publish `plugin.json` at the package root or declared path, and ensure every referenced native archive is
published at the URL recorded in the manifest. A pinned CLI entry has this shape:

```text
npm:@scope/plugin@1.2.3/plugin.json@<tarball-sha256>
```

When no explicit path is supplied, `dprint add npm:<package>` inspects the package and detects
`plugin.wasm` versus `plugin.json` automatically ([#1183]). Process plugins remain native and
platform-specific: npm transports the manifest, but does not make an absent platform binary exist.

## Checksums and install behavior

- Process plugins always require a checksum.
- Wasm checksums are optional, but `dprint add --checksum <plugin>` forces one ([#1184]).
- A registry-backed `dprint add <USER>/<short>` may write an npm specifier when `npm` metadata is present.
- A versionless `npm:<package>` resolves through nearby `node_modules`; a pinned specifier resolves from
  the registry. Test both if the README documents both.
- npm and proxy/GitHub artifacts are immutable. A bad artifact requires a version bump.

[#1184]: https://github.com/dprint/dprint/pull/1184

## Release verification

Use a permissive license by default, but preserve the wrapped or forked formatter's license and
copyright requirements; distribution through GitHub or npm does not change those obligations.

Run these against the published artifacts, not only local build outputs:

1. In a clean temporary project, run `dprint add <USER>/<short>` and verify the emitted source is the one
   intended by the registry metadata.
2. Run `dprint add --checksum <USER>/<short>` and format a fixture.
3. If npm is published, repeat with a pinned npm specifier and, when supported, a versionless local
   `node_modules` specifier.
4. Run `dprint config update --dry-run` and confirm the update URL, version, npm migration, and checksum
   behavior without rewriting the config ([#1156]).
5. For a process plugin, test every advertised platform entry in `plugin.json`; for a Wasm package meant
   for JavaScript, load it through `@dprint/formatter` as a separate gate.

[#1156]: https://github.com/dprint/dprint/pull/1156
