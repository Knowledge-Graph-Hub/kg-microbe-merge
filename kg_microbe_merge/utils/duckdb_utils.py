"""Utility functions for working with DuckDB in the KG Microbe Merge project."""

import os
from pathlib import Path
from typing import List

import duckdb

from kg_microbe_merge.constants import TMP_DIR


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


def merge_kg_tables(
    con, columns: List[str], base_table_name: str, subset_table_name: str, table_type: str
):
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
    if table_type == "nodes":
        con.execute("CREATE INDEX IF NOT EXISTS idx_combined_kg_nodes_id ON combined_kg_nodes(id);")
    elif table_type == "edges":
        con.execute(
            "CREATE INDEX IF NOT EXISTS idx_combined_kg_edges_subject ON combined_kg_edges(subject);"
        )
        con.execute(
            "CREATE INDEX IF NOT EXISTS idx_combined_kg_edges_object ON combined_kg_edges(object);"
        )
    con.execute(
        f"""CREATE INDEX IF NOT EXISTS idx_combined_kg_{table_type}_source_table
            ON combined_kg_{table_type}(source_table);"""
    )

    # Create merged graph table by prioritizing duplicate nodes/edges from base table using CTE
    if table_type == "nodes":
        partition_by = "id"
    elif table_type == "edges":
        partition_by = "subject, predicate, object"

    get_table_duplicates(con, "merged_kg", table_type, partition_by, base_table_name)
    get_table_duplicates(con, "duplicate", table_type, partition_by, base_table_name)

    drop_table(con, subset_table_name)
    drop_table(con, f"combined_kg_{table_type}")
    get_table_count(con, f"merged_kg_{table_type}")
    get_table_count(con, f"duplicate_{table_type}")

    return f"merged_kg_{table_type}", f"duplicate_{table_type}"


def get_table_duplicates(con, table_name, table_type, partition_by, base_table_name):
    """
    Get duplicates of rows in a given table.

    Creates table of both unique or duplicate values.

    # Example usage:
    # get_table_duplicates(con, "merged_kg", table_type, partition_by, base_table_name)
    # get_table_duplicates(con, "duplicate", table_type, partition_by, base_table_name)

    :param con: DuckDB connection object.
    :param table_name: Type of table ('merged_kg' or 'duplicate') to determine specific handling.
    :param table_type: Type of table ('nodes' or 'edges') to determine specific handling.
    :param partition_by: The columns that will be compared for finding duplicates.
    :param base_table_name: The name that will be used for the base table in duckdb.
    """
    if table_name == "merged_kg":
        condition = "rn = 1"
    elif table_name == "duplicate":
        condition = "rn > 1"

    con.execute(
        f"""
        CREATE OR REPLACE TABLE {table_name}_{table_type} AS
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
        WHERE {condition};
        """
    )


def write_file(con, columns, filename, table_name):
    """
    Output tsv file for given merged graph.

    :param columns: A list of columns in both the base and subset table.
    :type columns: List
    :param filename: Name of the output tsv file.
    :type filename: str
    :param table_name: The name used for the merged table in duckdb.
    :type table_name: Str
    """
    columns_str = ", ".join(columns)

    output_filename = os.getcwd() + "/" + filename

    con.execute(
        f"""
    COPY (
        SELECT {columns_str}
        FROM {table_name}
    ) TO '{output_filename}' WITH (FORMAT 'csv', DELIMITER '\t', HEADER true);
    """
    )


def load_into_duckdb(conn, file_list, table_name, exclude_columns=None):
    """
    Load multiple files into a single DuckDB table efficiently.
    """
    if exclude_columns is None:
        exclude_columns = []

    try:
        # Collect all unique columns from all files
        all_columns_set = set()
        file_columns_dict = {}

        for file in file_list:
            # Read the columns from the file without loading data
            columns_query = f"SELECT * FROM read_csv_auto('{file}', header=True, sep='\t') LIMIT 0"
            file_columns = conn.execute(columns_query).df().columns.tolist()
            file_columns_dict[file] = file_columns
            all_columns_set.update(file_columns)

        # Convert the set to a sorted list for consistent ordering
        all_columns = sorted(all_columns_set)

        # Exclude specified columns
        all_columns = [col for col in all_columns if col not in exclude_columns]

        # Create the table with all columns as VARCHAR
        create_table_query = f"""
        CREATE OR REPLACE TABLE {table_name} (
            {', '.join([f'"{col}" VARCHAR' for col in all_columns])}
        )
        """
        conn.execute(create_table_query)

        # Insert data from each file
        for file in file_list:
            file_columns = file_columns_dict[file]
            # Build the SELECT clause, inserting NULLs for missing columns
            select_parts = [
                f'"{col}"' if col in file_columns else f"NULL AS \"{col}\"" for col in all_columns
            ]
            select_str = ", ".join(select_parts)
            # Read data from the file and insert into the table
            insert_query = f"""
            INSERT INTO {table_name}
            SELECT {select_str}
            FROM read_csv_auto('{file}', header=True, sep='\t')
            """
            conn.execute(insert_query)

    except duckdb.Error as e:
        print(f"An error occurred while loading data into DuckDB: {e}")


def duckdb_nodes_merge(nodes_file_list, output_file, priority_sources):
    """
    Merge nodes files using DuckDB entirely in memory without batching.

    :param nodes_file_list: List of paths to nodes files.
    :param output_file: Path to the output file.
    :param priority_sources: List of source names to prioritize.
    """
    import duckdb
    import os
    from pathlib import Path

    # Create an in-memory DuckDB connection
    conn = duckdb.connect()

    # Load the files into DuckDB
    load_into_duckdb(conn, nodes_file_list, "combined_nodes")

    # Prepare the priority sources for SQL query
    priority_sources_str = ", ".join(f"'{source}'" for source in priority_sources)

    try:
        # Construct the query to get columns and their aggregation expressions
        query = f"""
        WITH columns AS (
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'combined_nodes'
        ),
        agg_columns AS (
            SELECT
                CASE
                    WHEN column_name = 'id' THEN 'id'
                    WHEN column_name = 'name' THEN
                        'COALESCE(MAX(CASE WHEN provided_by IN ({priority_sources_str}) THEN ' || column_name || ' END),
                                  MAX(' || column_name || ')) AS ' || column_name
                    ELSE 'STRING_AGG(DISTINCT ' || column_name || ", '|') AS " || column_name
                END AS agg_expr
            FROM columns
        )
        SELECT STRING_AGG(agg_expr, ', ') AS agg_expressions
        FROM agg_columns
        """

        # Execute the query to get the aggregation expressions
        agg_expressions = conn.execute(query).fetchone()[0]

        # Perform the aggregation over all data
        final_query = f"""
        SELECT {agg_expressions}
        FROM combined_nodes
        GROUP BY id
        ORDER BY id
        """

        # Print the generated SQL for debugging
        print("Generated SQL query:")
        print(final_query)

        # Execute the final query and write the result to the output file
        conn.execute(f"COPY ({final_query}) TO '{output_file}' (HEADER, DELIMITER '\t')")

        print(f"Merged file has been created as '{output_file}'")

    except duckdb.Error as e:
        print(f"An error occurred: {e}")
        print("Generated query was:")
        print(query)
    finally:
        # Close the connection
        conn.close()

def duckdb_nodes_merge_batch(nodes_file_list, output_file, priority_sources, batch_size=100000):
    """
    Merge nodes files using DuckDB with batching for large datasets.
    Optimizations:
    - Avoids using OFFSET in batch selection.
    - Uses temporary tables with row numbers for efficient batching.
    - Utilizes JOIN instead of IN for better performance.
    - Leverages DuckDB's multithreading capabilities.
    """
    import duckdb
    import os
    from pathlib import Path

    # Create a DuckDB connection
    merge_label = Path(output_file).parent.name
    nodes_db_file = f"{merge_label}_nodes.db"
    conn = duckdb.connect(nodes_db_file)

    # Load the files into DuckDB
    load_into_duckdb(conn, nodes_file_list, "combined_nodes")

    priority_sources_str = ", ".join(f"''{source}''" for source in priority_sources)

    try:
        # Construct the query to get columns and their aggregation expressions
        query = f"""
        WITH columns AS (
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'combined_nodes'
        ),
        agg_columns AS (
            SELECT
                CASE
                    WHEN column_name = 'id' THEN 'id'
                    WHEN column_name = 'name' THEN
                        'COALESCE(MAX(CASE WHEN provided_by IN ({priority_sources_str}) THEN ' || column_name || ' END),
                          ' || 'MAX(' || column_name || ')) AS ' || column_name
                    ELSE 'STRING_AGG(DISTINCT ' || column_name || ', ''|'' ORDER BY ' || column_name || ')
                    AS ' || column_name
                END AS agg_expr
            FROM columns
        )
        SELECT STRING_AGG(agg_expr, ', ') AS agg_expressions
        FROM agg_columns
        """

        # Execute the query to get the aggregation expressions
        agg_expressions = conn.execute(query).fetchone()[0]

        # Create a temporary table with row numbers for batching
        conn.execute("""
            CREATE TEMPORARY TABLE temp_ids AS
            SELECT id, ROW_NUMBER() OVER (ORDER BY id) AS rn
            FROM (SELECT DISTINCT id FROM combined_nodes)
        """)

        # Get the total number of unique IDs
        total_ids = conn.execute("SELECT COUNT(*) FROM temp_ids").fetchone()[0]

        # Process in batches without using OFFSET
        for batch_start in range(1, total_ids + 1, batch_size):
            batch_end = batch_start + batch_size - 1
            batch_query = f"""
            WITH batch_ids AS (
                SELECT id FROM temp_ids WHERE rn BETWEEN {batch_start} AND {batch_end}
            )
            SELECT {agg_expressions}
            FROM combined_nodes
            JOIN batch_ids USING (id)
            GROUP BY id
            ORDER BY id
            """

            # Print the generated SQL for debugging (only for the first batch)
            if batch_start == 1:
                print("Generated SQL query (for first batch):")
                print(batch_query)
                # For the first batch, create the file with headers
                conn.execute(f"COPY ({batch_query}) TO '{output_file}' (HEADER, DELIMITER '\t')")
            else:
                # For subsequent batches, append without headers
                batch_data = conn.execute(batch_query).fetch_df()
                batch_data.to_csv(output_file, mode="a", sep="\t", header=False, index=False)

            print(f"Processed {min(batch_end, total_ids)} / {total_ids} nodes")

        print(f"Merged file has been created as '{output_file}'")
    except duckdb.Error as e:
        print(f"An error occurred: {e}")
        print("Generated query was:")
        print(query)
    finally:
        # Close the connection
        conn.close()
        os.remove(nodes_db_file)

def duckdb_edges_merge(edges_file_list, output_file):
    """
    Merge edges files using DuckDB entirely in memory without batching.

    :param edges_file_list: List of paths to edges files.
    :param output_file: Path to the output file.
    """
    import duckdb
    import os

    # Create an in-memory DuckDB connection
    conn = duckdb.connect()

    try:
        # Load the files into DuckDB, excluding the 'id' column
        load_into_duckdb(conn, edges_file_list, "combined_edges", exclude_columns=["id"])

        # Get all column names except 'id'
        columns = conn.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'combined_edges' AND column_name != 'id'
        """).fetchall()
        column_names = [col[0] for col in columns]

        # Identify key columns and non-key columns
        key_columns = ['subject', 'predicate', 'object']
        non_key_columns = [col for col in column_names if col not in key_columns]

        # Construct aggregation expressions for non-key columns
        agg_expressions = []
        for col in non_key_columns:
            agg_expressions.append(
                f"STRING_AGG(DISTINCT {col}, '|' ORDER BY {col}) AS {col}"
            )

        # Construct the final query
        final_query = f"""
        SELECT
            {', '.join(key_columns)}
            {', ' + ', '.join(agg_expressions) if agg_expressions else ''}
        FROM combined_edges
        GROUP BY {', '.join(key_columns)}
        ORDER BY {', '.join(key_columns)}
        """

        # Print the generated SQL for debugging
        print("Generated SQL query:")
        print(final_query)

        # Execute the final query and write the result to the output file
        conn.execute(f"COPY ({final_query}) TO '{output_file}' (HEADER, DELIMITER '\t')")

        print(f"Merged file has been created as '{output_file}'")

    except duckdb.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

def duckdb_edges_merge_batch(edges_file_list, output_file, batch_size=1000000):
    """
    Merge edges files using DuckDB with optimized batching and aggregation.

    Optimizations:
    - Avoids using OFFSET in batch processing.
    - Uses temporary tables with row numbers for efficient batching.
    - Efficiently processes non-key columns without running out of memory.
    - Utilizes DuckDB's multithreading capabilities.
    """
    import duckdb
    import os
    from pathlib import Path

    # Create a DuckDB connection
    merge_label = Path(output_file).parent.name
    db_file = f"{merge_label}_edges_persistent.db"
    conn = duckdb.connect(db_file)

    try:
        # Load the files into DuckDB, excluding the 'id' column
        load_into_duckdb(conn, edges_file_list, "combined_edges", exclude_columns=["id"])

        # Get all column names except 'id'
        columns = conn.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'combined_edges' AND column_name != 'id'
        """).fetchall()
        column_names = [col[0] for col in columns]

        # Identify key columns and non-key columns
        key_columns = ['subject', 'predicate', 'object']
        non_key_columns = [col for col in column_names if col not in key_columns]

        # Construct aggregation expressions for non-key columns
        agg_expressions = []
        for col in non_key_columns:
            agg_expressions.append(
                f"STRING_AGG(DISTINCT {col}, '|' ORDER BY {col}) AS {col}"
            )

        # Create a temporary table with unique edges and row numbers for batching
        conn.execute(f"""
            CREATE TEMPORARY TABLE temp_edges AS
            SELECT {', '.join(key_columns)},
                   ROW_NUMBER() OVER (ORDER BY {', '.join(key_columns)}) AS rn
            FROM combined_edges
            GROUP BY {', '.join(key_columns)}
        """)

        # Get the total number of unique edges
        total_edges = conn.execute("SELECT COUNT(*) FROM temp_edges").fetchone()[0]

        # Process in batches without using OFFSET
        for batch_start in range(1, total_edges + 1, batch_size):
            batch_end = batch_start + batch_size - 1

            # Prepare the batch query
            batch_query = f"""
            WITH batch_edges AS (
                SELECT {', '.join(key_columns)}
                FROM temp_edges
                WHERE rn BETWEEN {batch_start} AND {batch_end}
            )
            SELECT
                {', '.join(key_columns)},
                {', '.join(agg_expressions)}
            FROM combined_edges
            INNER JOIN batch_edges USING ({', '.join(key_columns)})
            GROUP BY {', '.join(key_columns)}
            ORDER BY {', '.join(key_columns)}
            """

            # Print the generated SQL for debugging (only for the first batch)
            if batch_start == 1:
                print("Generated SQL query (for first batch):")
                print(batch_query)
                # For the first batch, create the file with headers
                conn.execute(f"COPY ({batch_query}) TO '{output_file}' (HEADER, DELIMITER '\t')")
            else:
                # For subsequent batches, append without headers
                batch_data = conn.execute(batch_query).fetch_df()
                batch_data.to_csv(output_file, mode="a", sep="\t", header=False, index=False)

            print(f"Processed {min(batch_end, total_edges)} / {total_edges} edges")

        print(f"Merged file has been created as '{output_file}'")

    except duckdb.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()
        os.remove(db_file)