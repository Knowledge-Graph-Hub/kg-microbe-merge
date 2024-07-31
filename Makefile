merge-kg-microbe-function:
	poetry run kg merge
	PWD=$(pwd)
	poetry run kg duckdb_merge -base-n $(PWD)/data/raw/nodes.tsv -subset-n $(PWD)/data/raw/nodes.tsv