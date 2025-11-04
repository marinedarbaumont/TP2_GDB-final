# Postgres ↔ Neo4j ↔ FastAPI (Docker Compose)


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

**1) Build & run**
```bash
docker compose up -d
```

**2) Open services**
- FastAPI: http://localhost:8000 (docs at /docs)
- Neo4j Browser: http://localhost:7474  (user: neo4j / pass: password)
- Postgres: localhost:5432 (user: app / pass: app / db: appdb)

**3) to check the health of the services:**
after the stack is up (app, postgres, neo4j)
```bash 
docker compose run --rm checks
```
**4) Screenshots of the Neo4j interface**

<img width="1376" height="523" alt="Screenshot 2025-11-03 at 14 18 44" src="https://github.com/user-attachments/assets/6406496f-9ab6-4564-9f92-a963e5f86b57" />

<img width="684" height="361" alt="Screenshot 2025-11-03 at 14 18 33" src="https://github.com/user-attachments/assets/b2fe1a58-4e26-493b-8a53-eb335f28da0b" />

<img width="947" height="372" alt="Screenshot 2025-11-03 at 14 18 27" src="https://github.com/user-attachments/assets/f9a5cb29-fc8d-4b90-8681-ecfa1276130c" />

<img width="773" height="363" alt="Screenshot 2025-11-03 at 14 18 37" src="https://github.com/user-attachments/assets/f5e7c3ac-8208-4884-b7f7-b8093ac03a8d" />
<img width="1370" height="387" alt="Screenshot 2025-11-03 at 14 19 38" src="https://github.com/user-attachments/assets/9008a478-6cb8-46b8-9aa7-b0cb35c7c2e5" />

**5) Screenshots of the health of my services**

<img width="638" height="35" alt="Screenshot 2025-11-03 at 14 20 21" src="https://github.com/user-attachments/assets/795b4ff8-458a-45cd-87eb-7cc5556dda67" />

<img width="354" height="299" alt="Screenshot 2025-11-04 at 09 22 42" src="https://github.com/user-attachments/assets/666af1cb-cf50-455f-a968-ae80509fbd1b" />

**6) Which recommendation strategy you can implement?
What’s improvements you’d make for transforming this mini project into production ready code ?**




