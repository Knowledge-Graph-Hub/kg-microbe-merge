
# download-transforms:

# 	wget "XXX" -O data/raw/merged-kg_nodes.tsv

# merge-kg-microbe-function:
# 	PWD=$(pwd)
# 	poetry run kg merge -y $(PWD)/merged_yamls/kg_base_merge.yaml
# 	poetry run kg duckdb_merge -base-n $(PWD)/data/merged/merged-kg_nodes.tsv -subset-n $(PWD)/data/transformed/nodes.tsv -base-e $(PWD)/data/merged/merged-kg_edges.tsv -subset-e $(PWD)/data/transformed/edges.tsv

# merge-kg-microbe-biomedical:
# 	PWD=$(pwd)
# 	poetry run kg merge -y $(PWD)/merged_yamls/kg_biomedical_merge.yaml

# merge-kg-microbe-biomedical-function:
# 	PWD=$(pwd)
# 	poetry run kg merge -y $(PWD)/merged_yamls/kg_biomedical_merge.yaml
# 	poetry run kg duckdb_merge -base-n $(PWD)/data/merged/merged-kg_nodes.tsv -subset-n $(PWD)/data/transformed/nodes.tsv -base-e $(PWD)/data/merged/merged-kg_edges.tsv -subset-e $(PWD)/data/transformed/edges.tsv

# !For testing
merge-kg-microbe-biomedical-function:
	poetry run kg merge -y merge_yamls/merge.yaml -m duckdb -base-n '/Users/brooksantangelo/Documents/LozuponeLab/FRMS_2024/duckdb/merged-kg_kg-microbe-base/merged-kg_nodes.tsv' -base-e '/Users/brooksantangelo/Documents/LozuponeLab/FRMS_2024/duckdb/merged-kg_kg-microbe-base/merged-kg_edges.tsv' -subset-n '/Users/brooksantangelo/Documents/Repositories/kg-microbe/data/transformed/uniprot_genome_features/nodes.tsv' -subset-e '/Users/brooksantangelo/Documents/Repositories/kg-microbe/data/transformed/uniprot_genome_features/edges.tsv'

# datamodel:
# 	poetry run gen-python $(PWD)/kg_microbe_merge/schema/merge_schema.yaml > $(PWD)/kg_microbe_merge/schema/merge_datamodel.py