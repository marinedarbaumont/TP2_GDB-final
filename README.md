# Postgres ↔ Neo4j ↔ FastAPI (Docker Compose)

Project scaffold that matches the structure you requested.

```
.
├─ docker-compose.yml
├─ postgres/
│  └─ init/
│     ├─ 01_schema.sql
│     └─ 02_seed.sql
├─ neo4j/
│  ├─ data/      # persisted DB files
│  └─ import/    # CSVs for direct Neo4j LOAD CSV
├─ app/
│  ├─ main.py           # FastAPI app
│  ├─ etl.py            # ETL from Postgres → Neo4j
│  ├─ queries.cypher
│  ├─ start.sh          # start uvicorn server
│  └─ requirements.txt  # libs
└─ README.md
```

## Quick start

1) Build & run
```bash
docker compose up -d
```

2) Open services
- FastAPI: http://localhost:8000 (docs at /docs)
- Neo4j Browser: http://localhost:7474  (user: neo4j / pass: Singapour.13)
- Postgres: localhost:5432 (user: app / pass: app / db: appdb)

3) to check the health of the services:
   # after the stack is up (app, postgres, neo4j)
```bash 
docker compose run --rm checks
```


