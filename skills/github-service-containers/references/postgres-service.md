# PostgreSQL Service Container

Complete workflow patterns for running PostgreSQL alongside GitHub Actions jobs.

## Container Job (Recommended)

Job runs in a Docker container. PostgreSQL accessed by label hostname, no port
mapping needed.

```yaml
name: PostgreSQL service example
on: push

jobs:
  container-job:
    runs-on: ubuntu-latest
    container: node:20-bookworm-slim

    services:
      postgres:
        image: postgres
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - name: Check out repository code
        uses: actions/checkout@v5

      - name: Install dependencies
        run: npm ci

      - name: Connect to PostgreSQL
        run: node client.js
        env:
          POSTGRES_HOST: postgres
          POSTGRES_PORT: 5432
```

**Key points:**

- `container: node:20-bookworm-slim` — job runs inside this container
- `POSTGRES_HOST: postgres` — hostname matches the service label
- `POSTGRES_PASSWORD: postgres` — required by the postgres image, set via `env:`
- No `ports:` needed — Docker bridge network handles connectivity

## Runner Job

Job runs directly on the runner machine. PostgreSQL accessed via `localhost`
with explicit port mapping.

```yaml
name: PostgreSQL Service Example
on: push

jobs:
  runner-job:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - name: Check out repository code
        uses: actions/checkout@v5

      - name: Install dependencies
        run: npm ci

      - name: Connect to PostgreSQL
        run: node client.js
        env:
          POSTGRES_HOST: localhost
          POSTGRES_PORT: 5432
```

**Key points:**

- No `container:` key — job runs on the runner directly
- `ports: ['5432:5432']` — required to expose PostgreSQL to the host
- `POSTGRES_HOST: localhost` — access via localhost, not label

## Health Check

```yaml
options: >-
  --health-cmd pg_isready
  --health-interval 10s
  --health-timeout 5s
  --health-retries 5
```

`pg_isready` checks if PostgreSQL is accepting connections. Pin a version
tag (e.g., `postgres:16`) for reproducible builds.

## Required Environment Variables

| Variable            | Where   | Value                    | Notes                      |
| ------------------- | ------- | ------------------------ | -------------------------- |
| `POSTGRES_PASSWORD` | Service | `postgres`               | Required by postgres image |
| `POSTGRES_HOST`     | Step    | `postgres` / `localhost` | Depends on job type        |
| `POSTGRES_PORT`     | Step    | `5432`                   | Default PostgreSQL port    |
| `POSTGRES_USER`     | Service | `postgres`               | Default (optional)         |
| `POSTGRES_DB`       | Service | `postgres`               | Default (optional)         |

## Test Script (Node.js)

Uses the `pg` npm package. Add to your repository as `client.js`:

```javascript
const { Client } = require('pg');

const pgclient = new Client({
	host: process.env.POSTGRES_HOST,
	port: process.env.POSTGRES_PORT,
	user: 'postgres',
	password: 'postgres',
	database: 'postgres',
});

pgclient.connect();

const table = 'CREATE TABLE student(id SERIAL PRIMARY KEY, firstName VARCHAR(40) NOT NULL, lastName VARCHAR(40) NOT NULL, age INT, address VARCHAR(80), email VARCHAR(40))';
const text = 'INSERT INTO student(firstname, lastname, age, address, email) VALUES($1, $2, $3, $4, $5) RETURNING *';
const values = [
	'Mona the',
	'Octocat',
	9,
	'88 Colin P Kelly Jr St, San Francisco, CA 94107',
	'octocat@github.com',
];

pgclient.query(table, (err, res) => {
	if (err) throw err;
});

pgclient.query(text, values, (err, res) => {
	if (err) throw err;
});

pgclient.query('SELECT * FROM student', (err, res) => {
	if (err) throw err;
	console.log(err, res.rows);
	pgclient.end();
});
```

Expected output:

```log
null [{
  id: 1,
  firstname: 'Mona the',
  lastname: 'Octocat',
  age: 9,
  address: '88 Colin P Kelly Jr St, San Francisco, CA 94107',
  email: 'octocat@github.com'
}]
```

## Gotchas

- **Missing `POSTGRES_PASSWORD`**: Container fails to start without it
- **No health check**: Steps may run before PostgreSQL accepts connections
- **Missing `ports:` on runner job**: PostgreSQL unreachable from host
- **Image tag**: `postgres` pulls latest. Pin to `postgres:16` for stability
- **Custom database**: Set `POSTGRES_DB` in service `env:` to create a named database

## See Also

- [redis-service.md](redis-service.md) - Redis service container
