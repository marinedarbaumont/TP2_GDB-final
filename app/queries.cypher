// --- Reset database ---
MATCH (n) DETACH DELETE n;

// --- Constraints & indexes ---
CREATE CONSTRAINT customer_id IF NOT EXISTS
FOR (c:Customer) REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT category_id IF NOT EXISTS
FOR (c:Category) REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT product_id IF NOT EXISTS
FOR (p:Product) REQUIRE p.id IS UNIQUE;

CREATE CONSTRAINT order_id IF NOT EXISTS
FOR (o:Order) REQUIRE o.id IS UNIQUE;

// Helpful indexes
CREATE INDEX product_category_id IF NOT EXISTS FOR (p:Product) ON (p.category_id);

