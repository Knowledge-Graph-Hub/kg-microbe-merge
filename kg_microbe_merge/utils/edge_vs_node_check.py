import duckdb
import argparse
import os

# Function to determine the category based on the ID prefix
def determine_category(node_id):
    category_mapping = {
        'EC:': 'biolink:Enzyme',
        'assay:': 'biolink:PhenotypicQuality',
        'trophic_type:': 'biolink:BiologicalProcess',
        'cell_shape:': 'biolink:PhenotypicQuality',
        'UniprotKB:': 'biolink:Enzyme',
        'medium:': 'biolink:ChemicalEntity',
        'carbon_substrates:': 'biolink:ChemicalEntity'
    }
    for prefix, category in category_mapping.items():
        if node_id.startswith(prefix):
            return category
    return 'Unknown'

def main(kg_path):

    # Connect to DuckDB (in-memory)
    con = duckdb.connect()

    # Load only the necessary columns from the TSV files into DuckDB tables
    con.execute(f"""
        CREATE TABLE edges AS 
        SELECT subject AS subject_id, object AS object_id 
        FROM read_csv_auto('data/merged/{kg_path}/merged-kg_edges.tsv', delim='\t', null_padding=true)
    """)
    con.execute(f"""
        CREATE TABLE nodes AS 
        SELECT id 
        FROM read_csv_auto('data/merged/{kg_path}/merged-kg_nodes.tsv', delim='\t', null_padding=true)
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
    missing_nodes_file = f'data/merged/{kg_path}/{kg_path}_missing_nodes.tsv'
    with open(missing_nodes_file, 'w') as f:
        f.write("id\n")  # Write header
        for row in missing_ids:
            if row[0] is not None:
                f.write(f"{row[0]}\n")

    # Write the missing IDs and their categories to a new TSV file
    missing_nodes_with_category_file = f'data/merged/{kg_path}/{kg_path}_missing_nodes_with_category.tsv'
    with open(missing_nodes_with_category_file, 'w') as f:
        for row in missing_ids:
            node_id = row[0]
            if node_id is not None:
                category = determine_category(node_id)
                # Write the id, category, and name columns, followed by the appropriate number of tab spaces
                f.write(f"{node_id}\t{category}\t\t\t\t\t\t\t\t\t\t\t\t\t\n")

    # Output the result
    if missing_ids:
        print(f"The following IDs are not represented as node IDs: {len(missing_ids)}")
    else:
        print("All subject and object IDs are represented as node IDs.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check for missing node IDs in the merged KG.')
    parser.add_argument('kg_path', type=str, help='Path to the merged KG directory')
    args = parser.parse_args()
    main(args.kg_path)