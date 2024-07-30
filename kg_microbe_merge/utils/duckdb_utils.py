import tempfile
import time
from pprint import pprint

import duckdb
from langchain_community.agent_toolkits import SQLDatabaseToolkit, create_sql_agent
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_openai import ChatOpenAI
from sqlalchemy import create_engine



NODES_COLUMNS = [
    "id", "name", "description", "category", "xref", "provided_by", "synonym", "object", "predicate", "relation", "same_as", "subject", "subsets"
]

nodes_columns_str = ", ".join(NODES_COLUMNS)

EDGES_COLUMNS = [
    "subject", "predicate", "object", "relation", "primary_knowledge_source"
]

edges_columns_str = ", ".join(EDGES_COLUMNS)

def duckdb_load_nodes(con, base_nodes_kg_file, subset_nodes_kg_file):

    # Read the subset file into a DuckDB table
    con.execute(f"""
    CREATE OR REPLACE TABLE base_nodes_kg AS
    SELECT NODES_COLUMNS
    FROM read_csv_auto('{base_nodes_kg_file}', delim='\t');
    """)
 
    # Read the base file into a DuckDB table
    con.execute(f"""
    CREATE OR REPLACE TABLE subset_nodes_kg AS
    SELECT NODES_COLUMNS
    FROM read_csv_auto('{subset_nodes_kg_file}', delim='\t');
    """)

    # Insert data from the base table into the subset table
    #con.execute("""
    #INSERT INTO merged_nodes_subset (NODES_COLUMNS)
    #SELECT NODES_COLUMNS
    #FROM merged_nodes_base;
    #""")

def duckdb_load_edges(con, merged_kg_edges_file, subset_kg_edges_file):

    # Read the subset edges file into a DuckDB table
    con.execute(f"""
    CREATE OR REPLACE TABLE merged_edges_subset AS
    SELECT EDGES_COLUMNS 
    FROM read_csv_auto('{subset_kg_edges_file}', delim='\t');
    """)

##append second file to first table, new column file name

    # Read the base edges file into a DuckDB table
    con.execute(f"""
    CREATE OR REPLACE TABLE merged_edges_base AS
    SELECT EDGES_COLUMNS
    FROM read_csv_auto('{merged_kg_edges_file}', delim='\t');
    """)

    # Insert data from the base edges table into the subset edges table
    #con.execute("""
    #INSERT INTO merged_edges_subset (EDGES_COLUMNS)
    #SELECT EDGES_COLUMNS
    #FROM merged_edges_base;
    #""")

def remove_duplicate_nodes(con, base_nodes_kg, subset_nodes_kg, final_kg):

    con.execute("""
    ALTER TABLE base_nodes_kg ADD COLUMN source_table VARCHAR(20);
    """)

    # Insert data from the base table into the subset table
    con.execute("""
    INSERT INTO '{base_nodes_kg}' (NODES_COLUMNS, source_table)
    SELECT NODES_COLUMNS, 'source_table'
    FROM '{subset_nodes_kg}';
    """)


#ALTER TABLE base_kg RENAME TO final_kg;
    con.execute("""
    ALTER TABLE {base_nodes_kg} RENAME TO {final_kg}
    """)

    ###drop two input tables

    # Step 1: Diagnostic select prefix and count duplicates
    prefix_duplicates = con.execute("""
    SELECT split_part(id, ':', 1) AS prefix, count(id) AS duplicates
    FROM (
        SELECT id, count(*) AS duplicate_count
        FROM {base_nodes_kg}
        GROUP BY id
        HAVING duplicate_count > 1
    )
    GROUP BY prefix;
    """).fetchdf()

    #Step 2: merge by removing duplicates
    con.execute("""
        CREATE OR REPLACE TABLE merged_nodes AS
        SELECT *
        FROM (
            SELECT *,
                -- Using a window function to assign a rank; rows from the base_nodes_kg are given higher priority
                ROW_NUMBER() OVER (
                    PARTITION BY id
                    ORDER BY CASE WHEN source_table = {base_nodes_kg} THEN 1 ELSE 2 END
                ) as rn
            FROM {final_kg}
        ) sub
        WHERE sub.rn = 1;
        """)

def remove_duplicate_edges(con, merged_edges_subset):

    # Step 1: Find duplicate edges
    duplicate_edges_query = f"""
    WITH DuplicateEdges AS (
        SELECT 
            subject, 
            object, 
            COUNT(*) AS duplicate_count
        FROM {merged_edges_subset}
        GROUP BY subject, object
        HAVING COUNT(*) > 1
    )
    SELECT 
        {merged_edges_subset}.{edges_columns_str}
        ??{merged_edges_subset}.filename    -- Including filename to see where the data is coming from
    FROM 
        {merged_edges_subset}
    INNER JOIN DuplicateEdges ON {merged_edges_subset}.subject = DuplicateEdges.subject AND {merged_edges_subset}.object = DuplicateEdges.object;
    """
    duplicate_edges = con.execute(duplicate_edges_query).fetchdf()

    # Step 2: Aggregate predicates for duplicated pairs and group by prefixes
    aggregated_predicates_query = f"""
    WITH DuplicatedPairs AS (
        SELECT
            split_part(subject, ':', 1) AS subject_prefix,
            split_part(object, ':', 1) AS object_prefix,
            subject,
            object
        FROM {merged_edges_subset}
        GROUP BY subject, object
        HAVING COUNT(*) > 1
    ),
    AggregatedPredicates AS (
        SELECT
            split_part(subject, ':', 1) AS subject_prefix,
            split_part(object, ':', 1) AS object_prefix,
            array_agg(DISTINCT predicate) AS predicates
        FROM {merged_edges_subset}
        WHERE EXISTS (
            SELECT 1
            FROM DuplicatedPairs
            WHERE DuplicatedPairs.subject = {merged_edges_subset}.subject AND DuplicatedPairs.object = {merged_edges_subset}.object
        )
        GROUP BY subject, object
    ),
    PrefixGroupedPredicates AS (
        SELECT
            subject_prefix,
            object_prefix,
            array_agg(DISTINCT predicates) AS grouped_predicates
        FROM AggregatedPredicates
        GROUP BY subject_prefix, object_prefix
    )
    SELECT
        subject_prefix,
        object_prefix,
        grouped_predicates
    FROM PrefixGroupedPredicates
    ORDER BY subject_prefix, object_prefix;
    """

def _import_nodes(self):
        columns_of_interest = ["id", "name"]
        with open(NODES_FILE, "r") as nodes_file:
            header_line = nodes_file.readline().strip().split("\t")
            column_indexes = {col: idx for idx, col in enumerate(header_line) if col in columns_of_interest}

            with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_nodes_file:
                temp_nodes_file.write("\t".join(columns_of_interest) + "\n")
                for line in nodes_file:
                    columns = line.strip().split("\t")
                    if len(columns) > max(column_indexes.values()):
                        node_id = columns[column_indexes["id"]]
                        node_label = columns[column_indexes["name"]]
                        temp_nodes_file.write(f"{node_id}\t{node_label}\n")
                temp_nodes_file.flush()

                # Load data from temporary file into DuckDB
                self.conn.execute(f"COPY nodes FROM '{temp_nodes_file.name}' (DELIMITER '\t', HEADER)")

def _import_edges(self):
    
        edge_column_of_interest = ["subject", "predicate", "object"]
        with open(EDGES_FILE, "r") as edges_file:
            header_line = edges_file.readline().strip().split("\t")
            column_indexes = {col: idx for idx, col in enumerate(header_line) if col in edge_column_of_interest}

            with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_edges_file:
                temp_edges_file.write("\t".join(edge_column_of_interest) + "\n")
                for line in edges_file:
                    columns = line.strip().split("\t")
                    source_id = columns[column_indexes["subject"]]
                    relationship = columns[column_indexes["predicate"]]
                    target_id = columns[column_indexes["object"]]
                    temp_edges_file.write(f"{source_id}\t{relationship}\t{target_id}\n")
                temp_edges_file.flush()

                # Load data from temporary file into DuckDB
                self.conn.execute(f"COPY edges FROM '{temp_edges_file.name}' (DELIMITER '\t', HEADER)")