# Distribution, registry metadata, and npm

Read this when publishing a plugin, adding it to the registry, or deciding whether to ship an npm
package. Keep these four surfaces distinct:

1. **Proxy name** — `dprint add <USER>/<short>` is the stable user-facing command.
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

Keep the committed registry entry, dynamically served metadata, and plugin `latest.json` distinct:

- Current source entries in `dprint/plugins`'s `info.json` carry `name`, `description`, `selected`, `configKey`,
  `keywords`, `fileExtensions`, `configExcludes`, and optional `website`, `fileNames`, `npm`,
  `defaultConfig`, and `configItems`. Do not add release-derived `version`, `url`, or `checksum` there;
  the service resolves current release/npm data dynamically.
- The plugin's served `latest.json` carries required `schemaVersion: 1`, `version`, and `url`, plus
  optional `checksum` and `npm`. Omitting `schemaVersion` makes a hand-hosted equivalent invalid.
- `npm` has `{ "name": "<package>" }`; add `path` when the plugin is not at the package root. The proxy
  derives `latest.json`'s declaration from the registry entry, while its served `info.json` additionally
  resolves npm's latest version ([dprint/plugins#71], [dprint/plugins#72]).
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
[dprint/plugins#71]: https://github.com/dprint/plugins/pull/71
[dprint/plugins#72]: https://github.com/dprint/plugins/pull/72

When `npm` is declared, dprint resolves the version from npm's `dist-tags.latest`, not the possibly stale
version in `info.json` or `latest.json`. Publish the npm version before advertising it in registry
metadata. A malformed or unreachable npm declaration falls back differently by command, so test `init`,
`add`, and `config update` rather than assuming one happy path.

## Proxy asset routing

The proxy resolves versioned `plugin.wasm`, `plugin.json`, and `schema.json` assets from any public GitHub
repository. A `dprint-plugin-` repo prefix is optional; it only enables the shorter repo name in proxy
URLs. Tags may contain letters, digits, `_`, and `.`, but not `-`; keep the bare-version house convention.

Non-Wasm assets have an extra boundary:

- Non-Wasm URLs, including `plugin.json`, `schema.json`, and native archives, are redirected through the
  proxy's `/asset/` route. This also lets relative manifest URLs resolve against a release-scoped location
  ([dprint/plugins#42]).
- dprint-owned repositories are served and persisted through R2 automatically. A community repository
  must open a PR adding its exact owner/repo to the asset allowlist to receive the same direct serving;
  otherwise `/asset/` redirects to GitHub ([dprint/plugins#44], [dprint/plugins#57]).
- Keep absolute release URLs in `plugin.json` by default. If relying on proxy-relative assets, obtain
  approval and test every platform through the published proxy URL, including browser/CORS consumers.

[dprint/plugins#42]: https://github.com/dprint/plugins/pull/42
[dprint/plugins#44]: https://github.com/dprint/plugins/pull/44
[dprint/plugins#57]: https://github.com/dprint/plugins/pull/57

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
- The proxy derives a GitHub-backed plugin checksum only from the `plugin.wasm` or `plugin.json` release
  asset's GitHub `sha256:` digest. It no longer scrapes a checksum-looking value from release notes
  ([dprint/plugins#78]).
- A pinned npm process-plugin specifier requires the **npm package tarball's** SHA-256. That is distinct
  from the `plugin.json` hash, its per-platform archive hashes, and GitHub's release-asset digest. Hash the
  exact published tarball and test the complete specifier ([dprint/dprint#1183]). As of
  [dprint/plugins#72], the registry resolves only the npm version, so its displayed process-plugin
  specifier omits this mandatory checksum; do not copy that value as a complete install specifier.
- Wasm checksums are optional, but `dprint add --checksum <plugin>` forces one ([#1184]).
- A registry-backed `dprint add <USER>/<short>` may write an npm specifier when `npm` metadata is present.
- A versionless `npm:<package>` resolves through nearby `node_modules`; a pinned specifier resolves from
  the registry. Test both if the README documents both.
- npm and proxy/GitHub artifacts are immutable. A bad artifact requires a version bump.

[#1184]: https://github.com/dprint/dprint/pull/1184
[dprint/plugins#78]: https://github.com/dprint/plugins/pull/78

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
