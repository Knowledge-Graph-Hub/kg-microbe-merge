import duckdb

# Connect to DuckDB (in-memory)
con = duckdb.connect()

# Load only the necessary columns from the TSV files into DuckDB tables
con.execute("""
    CREATE TABLE edges AS 
    SELECT subject AS subject_id, object AS object_id 
    FROM read_csv_auto('data/merged/kg-microbe-biomedical-function-cat/merged-kg_edges.tsv', delim='\t', null_padding=true)
""")
con.execute("""
    CREATE TABLE nodes AS 
    SELECT id 
    FROM read_csv_auto('data/merged/kg-microbe-biomedical-function-cat/merged-kg_nodes.tsv', delim='\t', null_padding=true)
""")

# Check whether all subject and object IDs are represented as node IDs
query = """
WITH distinct_ids AS (
    SELECT DISTINCT subject_id AS id FROM edges
    UNION
    SELECT DISTINCT object_id AS id FROM edges
)
SELECT distinct_ids.id
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


# Define the category mapping based on the prefix
category_mapping = {
    'EC:': 'biolink:Enzyme',
    'assay:': 'biolink:PhenotypicQuality',
    'trophic_type:': 'biolink:BiologicalProcess',
    'cell_shape:': 'biolink:PhenotypicQuality',
    'UniprotKB:': 'biolink:Enzyme',
    'medium:': 'biolink:ChemicalEntity',
    'carbon_substrates:': 'biolink:ChemicalEntity'
}

# Function to determine the category based on the ID prefix
def determine_category(node_id):
    for prefix, category in category_mapping.items():
        if node_id.startswith(prefix):
            return category
    return 'Unknown'

# Write the missing IDs and their categories to a new TSV file
with open('missing_nodes_with_category.tsv', 'w') as f:
    for row in missing_ids:
        node_id = row[0]
        category = determine_category(node_id)
        f.write(f"{node_id}\t{category}\t\n")  # The name column is left empty

# Output the result
if missing_ids:
    print(f"The following IDs are not represented as node IDs: {len(missing_ids)} \n missing_ids")
else:
    print("All subject and object IDs are represented as node IDs.")