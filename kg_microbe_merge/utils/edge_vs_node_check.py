import duckdb

# Connect to DuckDB (in-memory)
con = duckdb.connect()

# Load the TSV files into DuckDB tables
con.execute("CREATE TABLE edges AS SELECT * FROM read_csv_auto('data/merged/kg-microbe-biomedical-function-cat/merged-kg_edges.tsv', delim='\t')")
con.execute("CREATE TABLE nodes AS SELECT * FROM read_csv_auto('data/merged/kg-microbe-biomedical-function-cat/merged-kg_nodes.tsv', delim='\t')")

# Check whether all subject and object IDs are represented as node IDs
query = """
WITH distinct_ids AS (
    SELECT DISTINCT subject_id AS id FROM edges
    UNION
    SELECT DISTINCT object_id AS id FROM edges
)
SELECT id
FROM distinct_ids
LEFT JOIN nodes ON distinct_ids.id = nodes.id
WHERE nodes.id IS NULL
"""

# Execute the query and fetch all results
missing_ids = con.execute(query).fetchall()

# Write the missing IDs directly to a TSV file
with open('missing_nodes.tsv', 'w') as f:
    f.write("id\n")  # Write header
    for row in missing_ids:
        f.write(f"{row[0]}\n")

# Output the result
if missing_ids:
    print("The following IDs are not represented as node IDs:", missing_ids)
else:
    print("All subject and object IDs are represented as node IDs.")