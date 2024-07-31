
# download-transforms:

# 	wget "XXX" -O data/raw/merged-kg_nodes.tsv

merge-kg-microbe-function:
	PWD=$(pwd)
	poetry run kg merge -y $(PWD)/merged_yamls/kg_base_merge.yaml
	poetry run kg duckdb_merge -base-n $(PWD)/data/merged/merged-kg_nodes.tsv -subset-n $(PWD)/data/transformed/nodes.tsv -base-e $(PWD)/data/merged/merged-kg_edges.tsv -subset-e $(PWD)/data/transformed/edges.tsv

merge-kg-microbe-biomedical:
	PWD=$(pwd)
	poetry run kg merge -y $(PWD)/merged_yamls/kg_biomedical_merge.yaml

merge-kg-microbe-biomedical-function:
	PWD=$(pwd)
	poetry run kg merge -y $(PWD)/merged_yamls/kg_biomedical_merge.yaml
	poetry run kg duckdb_merge -base-n $(PWD)/data/merged/merged-kg_nodes.tsv -subset-n $(PWD)/data/transformed/nodes.tsv -base-e $(PWD)/data/merged/merged-kg_edges.tsv -subset-e $(PWD)/data/transformed/edges.tsv

