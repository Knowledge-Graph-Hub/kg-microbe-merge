import os
from typing import List


def get_table_count(con, table):
    """Get the number of rows of a given duckdb table name."""
    # Execute the SQL query to count the rows
    result = con.execute(
        f"""
        SELECT COUNT(*) FROM {table};
    """
    ).fetchone()

    # Print the number of rows
    print(f"Number of rows in '{table}': {result[0]}")


def drop_table(con, table):
    """Drop a duckdb table from memory."""
    # Drop table
    con.execute(
        f"""
    DROP TABLE IF EXISTS {table};
    """
    )


def add_column(con, column_name, table_name, value):
    """Add a new column to a duckdb table with all the same value."""
    # Add new column to base file to specify kg type
    con.execute(
        f"""
    ALTER TABLE {table_name} ADD COLUMN {column_name} VARCHAR(20);
    UPDATE {table_name}
    SET {column_name} = {value};
    """
    )


def duckdb_prepare_tables(
    con, base_kg_file, subset_kg_file, base_table_name, subset_table_name, columns
):
    """
    Create duckDB tables for the given base and subset graphs.
    :param base_kg_file: The file path to the base kg nodes file.
    :type base_kg_file: Str
    :param subset_kg_file: The file path to the subset kg nodes file.
    :type subset_kg_file: Str
    :param base_table_name: The name that will be used for the base table in duckdb.
    :type base_table_name: Str
    :param subset_table_name: The name that will be used for the subset table in duckdb.
    :type subset_table_name: Str
    :param columns: A list of columns in both the base and subset table.
    :type columns: List
    """
    duckdb_load_table(con, base_kg_file, base_table_name, columns)
    duckdb_load_table(con, subset_kg_file, subset_table_name, columns)


def duckdb_load_table(con, file, table_name, columns):
    """Create a duckDB tables for any given graph."""
    columns_str = ", ".join(columns)

    # Read the subset file into a DuckDB table
    con.execute(
        f"""
    CREATE OR REPLACE TABLE {table_name} AS
    SELECT {columns_str}
    FROM read_csv_auto('{file}', delim='\t');
    """
    )

    get_table_count(con, table_name)

def merge_kg_tables(con, columns: List[str], base_table_name: str, subset_table_name: str, table_type: str):
    """
    De-duplicate and create merged table from the given base and subset graphs.

    # Example usage:
    # merged_nodes_table = merge_kg_tables(con, columns, base_table_name, subset_table_name, 'nodes')
    # merged_edges_table = merge_kg_tables(con, columns, base_table_name, subset_table_name, 'edges')
    
    :param con: DuckDB connection object.
    :param columns: A list of columns in both the base and subset table.
    :param base_table_name: The name that will be used for the base table in duckdb.
    :param subset_table_name: The name that will be used for the subset table in duckdb.
    :param table_type: Type of table ('nodes' or 'edges') to determine specific handling.

    :return: Name of the merged table.
    """
    add_column(con, "source_table", base_table_name, base_table_name)
    add_column(con, "source_table", subset_table_name, subset_table_name)

    columns_str = ", ".join(columns) + ", source_table"

    # Insert data from the subset table into the base table
    con.execute(
        f"""
        INSERT INTO {base_table_name} ({columns_str})
        SELECT {columns_str}
        FROM {subset_table_name};
        ALTER TABLE {base_table_name} RENAME TO combined_kg_{table_type};
        """
    )

    get_table_count(con, f"combined_kg_{table_type}")

    # Ensure relevant columns are indexed
    if table_type == 'nodes':
        con.execute(f"CREATE INDEX IF NOT EXISTS idx_combined_kg_nodes_id ON combined_kg_nodes(id);")
    elif table_type == 'edges':
        con.execute(f"CREATE INDEX IF NOT EXISTS idx_combined_kg_edges_subject ON combined_kg_edges(subject);")
        con.execute(f"CREATE INDEX IF NOT EXISTS idx_combined_kg_edges_object ON combined_kg_edges(object);")
    con.execute(f"CREATE INDEX IF NOT EXISTS idx_combined_kg_{table_type}_source_table ON combined_kg_{table_type}(source_table);")

    # Create merged graph table by prioritizing duplicate nodes/edges from base table using CTE
    if table_type == 'nodes':
        partition_by = "id"
    elif table_type == 'edges':
        partition_by = "subject, object"

    con.execute(
        f"""
        CREATE OR REPLACE TABLE merged_kg_{table_type} AS
        WITH ranked_{table_type} AS (
            SELECT *,
                ROW_NUMBER() OVER (
                    PARTITION BY {partition_by}
                    ORDER BY CASE WHEN source_table = '{base_table_name}' THEN 1 ELSE 2 END
                ) as rn
            FROM combined_kg_{table_type}
        )
        SELECT *
        FROM ranked_{table_type}
        WHERE rn = 1;
        """
    )

    drop_table(con, subset_table_name)
    drop_table(con, f"combined_kg_{table_type}")
    get_table_count(con, f"merged_kg_{table_type}")

    return f"merged_kg_{table_type}"



def write_file(con, columns, filename, merge_kg_table_name):
    """
    Output tsv file for given merged graph.
    :param columns: A list of columns in both the base and subset table.
    :type columns: List
    :param filename: Name of the output tsv file.
    :type filename: str
    :param merge_kg_table_name: The name used for the merged table in duckdb.
    :type merge_kg_table_name: Str
    """
    columns_str = ", ".join(columns)

    output_filename = os.getcwd() + "/" + filename

    con.execute(
        f"""
    COPY (
        SELECT {columns_str}
        FROM {merge_kg_table_name}
    ) TO '{output_filename}' WITH (FORMAT 'csv', DELIMITER '\t', HEADER true);
    """
    )
