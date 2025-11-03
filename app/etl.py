import os
import time
from pathlib import Path
from typing import Iterable, List

import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
from neo4j import GraphDatabase, basic_auth



# paths
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://app:app@postgres:5432/shop")
NEO4J_URL = os.getenv("NEO4J_URL", "bolt://neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "Singapour.13") or os.getenv("NEO4J_PASS") or "neo4j"

# Where the app writes CSVs 
CSV_DIR = Path("/neo4j_import")
CSV_DIR.mkdir(parents=True, exist_ok=True)



# Helpers
def wait_for_postgres(timeout: int = 60) -> None:
    """Poll Postgres until connectable."""
    start = time.time()
    last_err = None
    while time.time() - start < timeout:
        try:
            with psycopg2.connect(DATABASE_URL) as _conn:
                return
        except Exception as e:
            last_err = e
            time.sleep(1)
    raise RuntimeError(f"Postgres not ready after {timeout}s: {last_err}")


def wait_for_neo4j(timeout: int = 60) -> None:
    """Poll Neo4j until connectable."""
    start = time.time()
    last_err = None
    while time.time() - start < timeout:
        try:
            driver = GraphDatabase.driver(
                NEO4J_URL, auth=basic_auth(NEO4J_USER, NEO4J_PASSWORD)
            )
            with driver.session() as session:
                session.run("RETURN 1").consume()
            driver.close()
            return
        except Exception as e:
            last_err = e
            time.sleep(1)
    raise RuntimeError(f"Neo4j not ready after {timeout}s: {last_err}")


def run_cypher(query: str, params: dict | None = None) -> None:
    driver = GraphDatabase.driver(NEO4J_URL, auth=basic_auth(NEO4J_USER, NEO4J_PASSWORD))
    try:
        with driver.session() as session:
            session.run(query, params or {}).consume()
    finally:
        driver.close()


def run_cypher_file(path: Path) -> None:
    """
    Executes multiple Cypher statements from a file.
    Splits on semicolons that end a line (simple & effective for this TP).
    """
    text = path.read_text(encoding="utf-8")
    statements: List[str] = []
    buf: List[str] = []

    for line in text.splitlines():
        # strip // comments to keep queries accessible and readable
        if line.strip().startswith("//"):
            continue
        buf.append(line)
        if line.rstrip().endswith(";"):
            statements.append("\n".join(buf).rstrip(";").strip())
            buf = []
    if buf:
        statements.append("\n".join(buf).strip())

    for stmt in statements:
        if stmt:
            run_cypher(stmt)


def chunk(df: pd.DataFrame, size: int) -> Iterable[pd.DataFrame]:
    """Yield df in chunks of 'size' rows."""
    for start in range(0, len(df), size):
        yield df.iloc[start : start + size]



# Main ETL
def etl() -> dict:
    """
    Extract from Postgres -> CSVs -> LOAD CSV into Neo4j
    Creates:
      - (:Category {id,name})
      - (:Product {id,name,price,category_id})-[:IN_CATEGORY]->(:Category)
      - (:Customer {id,name,join_date})
      - (:Order {id,ts}) with (Customer)-[:PLACED]->(Order)
      - (Order)-[:CONTAINS {quantity}]->(Product)
      - (Customer)-[:VIEW|:CLICK|:ADD_TO_CART {ts}]->(Product) via APOC
    """
    # Wait for services
    wait_for_postgres()
    wait_for_neo4j()

    # Extract from Postgres
    tables = [
        "customers",
        "categories",
        "products",
        "orders",
        "order_items",
        "events",
    ]
    dfs: dict[str, pd.DataFrame] = {}

    with psycopg2.connect(DATABASE_URL) as conn:
        for t in tables:
            dfs[t] = pd.read_sql_query(f"SELECT * FROM {t};", conn)

    # LOAD CSV
    files = {}
    for name, df in dfs.items():
        path = CSV_DIR / f"{name}.csv"
        
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        df.to_csv(path, index=False)
        files[name] = path.name  

    # Prepare Neo4j schema
    queries_path = Path(__file__).with_name("queries.cypher")
    run_cypher_file(queries_path)

    # Load nodes
    # Categories
    run_cypher(f"""
    CALL {{
    LOAD CSV WITH HEADERS FROM 'file:///{files["categories"]}' AS row
    MERGE (c:Category {{id: row.id}})
    SET c.name = row.name
    }} IN TRANSACTIONS OF 1000 ROWS
    RETURN 0 AS done
    """)

    # Products (+ IN_CATEGORY link)
    run_cypher(f"""
    CALL {{
    LOAD CSV WITH HEADERS FROM 'file:///{files["products"]}' AS row
    MERGE (p:Product {{id: row.id}})
    SET p.name = row.name,
        p.price = toFloat(row.price),
        p.category_id = row.category_id
    WITH p, row
    MATCH (cat:Category {{id: row.category_id}})
    MERGE (p)-[:IN_CATEGORY]->(cat)
    }} IN TRANSACTIONS OF 1000 ROWS
    RETURN 0 AS done
    """)

    # Customers
    run_cypher(f"""
    CALL {{
    LOAD CSV WITH HEADERS FROM 'file:///{files["customers"]}' AS row
    MERGE (c:Customer {{id: row.id}})
    SET c.name = row.name,
        c.join_date = date(row.join_date)
    }} IN TRANSACTIONS OF 1000 ROWS
    RETURN 0 AS done
    """)

    # Orders (+ PLACED by Customer)
    run_cypher(f"""
    CALL {{
    LOAD CSV WITH HEADERS FROM 'file:///{files["orders"]}' AS row
    MERGE (o:Order {{id: row.id}})
    SET o.ts = datetime(row.ts)
    WITH o, row
    MATCH (c:Customer {{id: row.customer_id}})
    MERGE (c)-[:PLACED]->(o)
    }} IN TRANSACTIONS OF 1000 ROWS
    RETURN 0 AS done
    """)

    # Order items (CONTAINS)
    run_cypher(f"""
    CALL {{
    LOAD CSV WITH HEADERS FROM 'file:///{files["order_items"]}' AS row
    MATCH (o:Order {{id: row.order_id}})
    MATCH (p:Product {{id: row.product_id}})
    MERGE (o)-[r:CONTAINS]->(p)
    SET r.quantity = toInteger(row.quantity)
    }} IN TRANSACTIONS OF 1000 ROWS
    RETURN 0 AS done
    """)

    # Events via APOC
    run_cypher(f"""
    CALL {{
    LOAD CSV WITH HEADERS FROM 'file:///{files["events"]}' AS row
    MATCH (c:Customer {{id: row.customer_id}})
    MATCH (p:Product {{id: row.product_id}})
    WITH c, p, toUpper(row.event_type) AS etype, datetime(row.ts) AS ts
    CALL apoc.create.relationship(c, etype, {{ts: ts}}, p) YIELD rel
    RETURN 0 AS dummy
    }} IN TRANSACTIONS OF 1000 ROWS
    RETURN 0 AS done
    """)

    # Return summary
    return {
        "rows": {k: int(v.shape[0]) for k, v in dfs.items()},
        "csv_dir": str(CSV_DIR),
        "status": "ok",
    }





if __name__ == "__main__":
    out = etl()
    print(out)
