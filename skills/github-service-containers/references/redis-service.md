# Redis Service Container

Complete workflow patterns for running Redis alongside GitHub Actions jobs.

## Container Job (Recommended)

Job runs in a Docker container. Redis accessed by label hostname, no port
mapping needed.

```yaml
name: Redis container example
on: push

jobs:
  container-job:
    runs-on: ubuntu-latest
    container: node:20-bookworm-slim

    services:
      redis:
        image: redis
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - name: Check out repository code
        uses: actions/checkout@v5

      - name: Install dependencies
        run: npm ci

      - name: Connect to Redis
        run: node client.js
        env:
          REDIS_HOST: redis
          REDIS_PORT: 6379
```

**Key points:**

- `container: node:20-bookworm-slim` — job runs inside this container
- `REDIS_HOST: redis` — hostname matches the service label
- No `ports:` needed — Docker bridge network exposes all ports between containers

## Runner Job

Job runs directly on the runner machine. Redis accessed via `localhost` with
explicit port mapping.

```yaml
name: Redis runner example
on: push

jobs:
  runner-job:
    runs-on: ubuntu-latest

    services:
      redis:
        image: redis
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - name: Check out repository code
        uses: actions/checkout@v5

      - name: Install dependencies
        run: npm ci

      - name: Connect to Redis
        run: node client.js
        env:
          REDIS_HOST: localhost
          REDIS_PORT: 6379
```

**Key points:**

- No `container:` key — job runs on the runner directly
- `ports: ['6379:6379']` — required to expose Redis to the host
- `REDIS_HOST: localhost` — access via localhost, not label

## Health Check

```yaml
options: >-
  --health-cmd "redis-cli ping"
  --health-interval 10s
  --health-timeout 5s
  --health-retries 5
```

`redis-cli ping` returns `PONG` when Redis is ready. Pin a version tag
(e.g., `redis:7`) for reproducible builds.

## Environment Variables

| Variable     | Container Job | Runner Job  |
| ------------ | ------------- | ----------- |
| `REDIS_HOST` | `redis`       | `localhost` |
| `REDIS_PORT` | `6379`        | `6379`      |

## Test Script (Node.js)

Uses the `redis` npm package. Add to your repository as `client.js`:

```javascript
const redis = require('redis');

const redisClient = redis.createClient({
	url: `redis://${process.env.REDIS_HOST}:${process.env.REDIS_PORT}`,
});

redisClient.on('error', (err) => console.log('Error', err));

(async () => {
	await redisClient.connect();

	const setReply = await redisClient.set('octocat', 'Mona the Octocat');
	console.log('Reply: ' + setReply);

	const hashReply = await redisClient.hSet('species', 'octocat', 'Cat and Octopus');
	console.log('Reply: ' + hashReply);

	const keys = await redisClient.hKeys('species');
	console.log(keys.length + ' replies:');
	keys.forEach((key, i) => console.log('    ' + i + ': ' + key));

	await redisClient.quit();
})();
```

Expected output:

```log
Reply: OK
Reply: 1
3 replies:
    0: octocat
    1: dinotocat
    2: robotocat
```

## Gotchas

- **No health check**: Steps may run before Redis is ready, causing ECONNREFUSED
- **Missing `ports:` on runner job**: Redis unreachable from host
- **Image tag**: `redis` pulls latest. Pin to `redis:7` for stability
- **Multiple Redis instances**: Use different labels and ports

## See Also

- [postgres-service.md](postgres-service.md) - PostgreSQL service container
