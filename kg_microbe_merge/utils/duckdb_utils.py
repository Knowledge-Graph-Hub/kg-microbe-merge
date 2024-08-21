"""Utility functions for working with DuckDB in the KG Microbe Merge project."""

import os
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
    Load multiple files into a single DuckDB table.

    :param conn: DuckDB connection object.
    :param file_list: List of file paths to load.
    :param table_name: Name of the table to create.
    :param exclude_columns: List of columns to exclude from the table.
    """
    if exclude_columns is None:
        exclude_columns = []

    # Collect all columns from all files
    all_columns = []
    file_columns_dict = {}

    for idx, file in enumerate(file_list):
        columns_query = f"SELECT * FROM read_csv_auto('{file}', header=true, sep='\t') LIMIT 0"
        all_columns = conn.execute(columns_query).df().columns.tolist()
        file_columns_dict[file] = all_columns
        if idx == 0:
            all_columns.extend(all_columns)
        else:
            all_columns.extend([col for col in all_columns if col not in all_columns])

    # Read the structure of the first file to get column names
    all_columns = conn.execute(columns_query).df().columns.tolist()

    # Filter out excluded columns
    all_columns = [col for col in all_columns if col not in exclude_columns]
    # columns_str = ", ".join(all_columns)

    create_table_query = f"""CREATE OR REPLACE TABLE {table_name}
                                 ({', '.join([f'{col} VARCHAR' for col in all_columns])})"""
    print(f"Create Table Query: {create_table_query}")  # Debugging line
    conn.execute(create_table_query)

    # Insert data from each file
    for file in file_list:
        file_columns = file_columns_dict[file]
        select_parts = [
            f"{col}" if col in file_columns else f"NULL AS {col}" for col in all_columns
        ]
        select_str = ", ".join(select_parts)
        insert_query = f"""INSERT INTO {table_name} SELECT {select_str} FROM read_csv_auto('{file}',
                                 header=true, sep='\t')"""
        print(f"Insert Query: {insert_query}")  # Debugging line
        conn.execute(insert_query)

    print(f"Loaded {len(file_list)} files into table '{table_name}'")


def duckdb_nodes_merge(nodes_file_list, output_file, priority_sources, batch_size=100000):
    """
    Merge nodes files using DuckDB with batching for large datasets.

    Construct the query to merge the nodes

    This query performs the following operations:
    1. WITH columns AS (...):
       - Retrieves all column names from the 'combined_nodes' table.

    2. WITH agg_columns AS (...):
       - Generates aggregation expressions for each column:
         a. For 'id': Keep as is (used for grouping)
         b. For 'name':
            - If any row for this id has 'provided_by' matching any value in the priority_sources list,
              select the 'name' from that row.
            - Otherwise, select the first 'name' encountered.
         c. For all other columns:
            - Concatenate all distinct values with '|' as separator.

    3. SELECT STRING_AGG(...):
       - Combines all aggregation expressions into a single string.

    4. The resulting aggregation expressions are then used in a batched processing approach:
       - Divide the data into batches based on unique IDs.
       - For each batch:
         a. Select the relevant IDs.
         b. Apply the aggregation expressions.
         c. Group by ID and order the results.
         d. Write the results to the output file.

    This batched approach allows for processing of large datasets by:
    - Reducing memory usage by processing subsets of data at a time.
    - Maintaining the same aggregation logic as the original query.
    - Ensuring consistent output formatting across all batches.

    :param nodes_file_list: List of paths to nodes files.
    :param output_file: Path to the output file.
    :param priority_sources: List of source names to prioritize.
    """
    # Create a DuckDB connection
    conn = duckdb.connect("nodes.db")

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

        # Get the total number of unique IDs
        total_ids = conn.execute("SELECT COUNT(DISTINCT id) FROM combined_nodes").fetchone()[0]

        # Process in batches
        for offset in range(0, total_ids, batch_size):
            batch_query = f"""
            WITH batch_ids AS (
                SELECT DISTINCT id
                FROM combined_nodes
                ORDER BY id
                LIMIT {batch_size} OFFSET {offset}
            )
            SELECT {agg_expressions}
            FROM combined_nodes
            WHERE id IN (SELECT id FROM batch_ids)
            GROUP BY id
            ORDER BY id
            """

            # Print the generated SQL for debugging (only for the first batch)
            if offset == 0:
                print("Generated SQL query (for first batch):")
                print(batch_query)
                # For the first batch, create the file with headers
                conn.execute(f"COPY ({batch_query}) TO '{output_file}' (HEADER, DELIMITER '\t')")

            else:
                # For subsequent batches, append without headers
                batch_data = conn.execute(batch_query).fetch_df()
                batch_data.to_csv(output_file, mode="a", sep="\t", header=False, index=False)

            print(f"Written {min(offset + batch_size, total_ids)} / {total_ids} nodes")

        print(f"Merged file has been created as '{output_file}'")
    except duckdb.Error as e:
        print(f"An error occurred: {e}")
        print("Generated query was:")
        print(query)
    finally:
        # Close the connection
        conn.close()
        os.remove("nodes.db")


def duckdb_edges_merge(edges_file_list, output_file, batch_size=1000000):
    """
    Merge edges files using DuckDB with a disk-based approach for improved memory efficiency.

    :param edges_file_list: List of paths to edges files.
    :param output_file: Path to the output file.
    :param batch_size: Number of edges to process in each batch.

    Detailed Explanation:

    1. Initial Setup:
       - The function connects to a persistent DuckDB database on disk.
       - It loads the edge files into a table using a memory-mapped approach.

    2. Temporary Table Creation:
       - A temporary table is created with distinct subject, predicate, and object combinations.
       - This table is stored on disk using a memory-mapped file.

    3. Batched Column-wise Processing:
       - For each non-key column (not subject, predicate, or object):
         - The column is added to the temporary table.
         - An UPDATE statement aggregates the distinct values for each edge in batches.

    4. Result Writing:
       - The final results are written to the output file directly from the temporary table.

    5. Error Handling and Cleanup:
       - Any DuckDB errors are caught and reported.
       - The database connection is closed and temporary files are removed.

    This approach processes data in batches and uses disk storage, which significantly reduces
    memory usage and allows for processing of very large datasets that exceed available RAM.
    """
    os.makedirs(TMP_DIR, exist_ok=True)
    db_file = "edges_persistent.db"
    conn = duckdb.connect(db_file)

    try:
        # Enable memory-mapped storage for temporary tables
        conn.execute(f"PRAGMA temp_directory='{TMP_DIR}'")  # Store temp files in the same directory
        # conn.execute("PRAGMA memory_limit='4GB'")  # Adjust based on available system memory

        # Load the files into DuckDB, excluding the 'id' column
        load_into_duckdb(conn, edges_file_list, "combined_edges", exclude_columns=["id"])

        # ! Commented because for now we don't care about columns other than subject, predicate, and object.
        # # Get column names
        # columns = conn.execute(
        #     "SELECT column_name FROM information_schema.columns WHERE table_name = 'combined_edges'"
        # ).fetchall()
        # column_names = [col[0] for col in columns]

        # Create a temporary table for storing intermediate results
        conn.execute(
            """
            CREATE OR REPLACE TABLE temp_edges AS
            SELECT DISTINCT subject, predicate, object
            FROM combined_edges
        """
        )

        # Process non-key columns in batches
        # ! This approach is not efficient for large datasets and may run out of memory
        # for column in column_names:
        #     if column not in ("subject", "predicate", "object"):
        #         conn.execute(f"ALTER TABLE temp_edges ADD COLUMN {column} STRING")

        #         # Process in batches
        #         offset = 0
        #         while True:
        #             batch_update = conn.execute(
        #                 f"""
        #                 UPDATE temp_edges
        #                 SET {column} = (
        #                     SELECT string_agg(DISTINCT ce.{column}, '|' ORDER BY ce.{column})
        #                     FROM (
        #                         SELECT subject, predicate, object, {column}
        #                         FROM combined_edges
        #                         LIMIT {batch_size} OFFSET {offset}
        #                     ) ce
        #                     WHERE ce.subject = temp_edges.subject
        #                       AND ce.predicate = temp_edges.predicate
        #                       AND ce.object = temp_edges.object
        #                 )
        #                 WHERE temp_edges.rowid IN (
        #                     SELECT rowid
        #                     FROM temp_edges
        #                     LIMIT {batch_size} OFFSET {offset}
        #                 )
        #             """
        #             )

        #             if batch_update.fetchone()[0] == 0:
        #                 break

        #             offset += batch_size
        #             print(f"Processed {offset} rows for column {column}")

        # Write results to file in batches
        with open(output_file, "w") as f:
            # Write header
            header = conn.execute("SELECT * FROM temp_edges LIMIT 0").fetchdf().columns.tolist()
            f.write("\t".join(header) + "\n")

            # Write data in batches
            offset = 0
            while True:
                batch = conn.execute(
                    f"""
                    SELECT *
                    FROM temp_edges
                    ORDER BY subject, predicate, object
                    LIMIT {batch_size} OFFSET {offset}
                """
                ).fetchdf()

                if batch.empty:
                    break

                batch.to_csv(f, sep="\t", header=False, index=False, mode="a")
                offset += batch_size
                print(f"Written {offset} rows to output file")

        print(f"Merged file has been created as '{output_file}'")

    except duckdb.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()
        os.remove(db_file)
