# Dockerfile Patterns for GitHub Actions

Dockerfile templates, base image selection, and common pitfalls.

## Starter Template

```dockerfile
# Container image that runs your code
FROM alpine:3.21

# Copies your code file from your action repository to the filesystem path `/`
COPY entrypoint.sh /entrypoint.sh

# Code file to execute when the docker container starts up
ENTRYPOINT ["/entrypoint.sh"]
```

## Key Rules

| Rule                        | Detail                                                              |
| --------------------------- | ------------------------------------------------------------------- |
| Use `ENTRYPOINT`, not `CMD` | GitHub Actions requires `ENTRYPOINT` for execution                  |
| `COPY` before `ENTRYPOINT`  | File must exist at build time                                       |
| Pin image tags              | Use `alpine:3.21`, never `alpine:latest`                            |
| Capitalize `Dockerfile`     | Capital `D`, lowercase `f` — required on case-sensitive filesystems |

## Base Image Selection

| Image         | Use Case                          | Size    |
| ------------- | --------------------------------- | ------- |
| `alpine`      | Shell scripts, lightweight tools  | ~5 MB   |
| `node:slim`   | JavaScript/TypeScript actions     | ~60 MB  |
| `python:slim` | Python-based actions              | ~45 MB  |
| `golang`      | Go actions (compile in container) | ~300 MB |
| `ubuntu`      | Actions needing apt packages      | ~30 MB  |

Prefer slim/alpine variants for faster pull times in CI.

## Common Patterns

### With package dependencies

```dockerfile
FROM alpine:3.21

RUN apk add --no-cache \
    curl \
    jq \
    bash

COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
```

### Multi-stage build (compiled language)

```dockerfile
FROM golang:1.22 AS builder
WORKDIR /app
COPY . .
RUN go build -o /action ./cmd/main.go

FROM alpine:3.21
COPY --from=builder /action /action
ENTRYPOINT ["/action"]
```

### With environment variables

```dockerfile
FROM alpine:3.21

ENV MY_VAR="default_value"

COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
```

## Container Filesystem

When running a Docker container action, GitHub maps directories:

| Host (Runner)       | Container                | Purpose       |
| ------------------- | ------------------------ | ------------- |
| `$GITHUB_WORKSPACE` | `/github/workspace`      | Repo checkout |
| `$GITHUB_OUTPUT`    | `/github/file_commands/` | Output file   |
| `$GITHUB_ENV`       | `/github/file_commands/` | Env var file  |

Files written to `/github/workspace` are available to subsequent steps.

## Gotchas

- **No `USER` instruction**: Actions run as root by default. Adding a `USER`
  may cause permission issues with workspace mounting.
- **No `WORKDIR /github/workspace`**: The workspace is mounted at runtime,
  not at build time. Setting `WORKDIR` won't persist.
- **Layer caching**: GitHub rebuilds the image on every run unless you use a
  pre-built image (`image: 'docker://ghcr.io/org/image:tag'`).
- **File permissions**: If `entrypoint.sh` isn't executable, the container
  will fail to start. Use `git update-index --chmod=+x` before committing.

## See Also

- [action-metadata.md](action-metadata.md) - Connecting Dockerfile to action.yml
- [entrypoint-scripts.md](entrypoint-scripts.md) - Writing the entrypoint
