import os

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
    ALTER TABLE {table_name} ADD COLUMN source_table VARCHAR(20);
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

def merge_kg_nodes_tables(con, columns, base_table_name, subset_table_name):
    """
    De-duplicate and create merged table from the given base and subset graphs.
    :param base_table_name: The name that will be used for the base table in duckdb.
    :type base_table_name: Str
    :param subset_table_name: The name that will be used for the subset table in duckdb.
    :type subset_table_name: Str
    :param columns: A list of columns in both the base and subset table.
    :type columns: List
    """
    add_column(con, "source_table", base_table_name, base_table_name)
    add_column(con, "source_table", subset_table_name, subset_table_name)

    nodes_columns_str = ", ".join(columns)
    nodes_columns_str = nodes_columns_str + ", source_table"

    # Insert data from the subset table into the base table
    con.execute(
        f"""
    INSERT INTO {base_table_name} ({nodes_columns_str})
    SELECT {nodes_columns_str}
    FROM {subset_table_name};
    ALTER TABLE {base_table_name} RENAME TO combined_kg_nodes
    """
    )

    get_table_count(con, "combined_kg_nodes")

    # Create merged graph table by prioritizing duplicate nodes from base table
    con.execute(
        f"""
        CREATE OR REPLACE TABLE merged_kg_nodes AS
        SELECT *
        FROM (
            SELECT *,
                ROW_NUMBER() OVER (
                    PARTITION BY id
                    ORDER BY CASE WHEN source_table = '{base_table_name}' THEN 1 ELSE 2 END
                ) as rn
            FROM combined_kg_nodes
        ) sub
        WHERE sub.rn = 1;
        """
    )

    drop_table(con, subset_table_name)
    drop_table(con, "combined_kg_nodes")
    get_table_count(con, "merged_kg_nodes")

    return "merged_kg_nodes"

# def merge_kg_edges_tables(con, columns, base_table_name, subset_table_name):


def write_file(con, columns, filename, merge_kg_table_name):
    """
    Output tsv file for given merged graph.
    :param columns: A list of columns in both the base and subset table.
    :type columns: List
    :param filename: Name of the output tsv file.
    :type filename: Str
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