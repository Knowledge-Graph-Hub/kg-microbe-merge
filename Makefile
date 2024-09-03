
datamodel:
	poetry run gen-python kg_microbe_merge/schema/merge_schema.yaml > kg_microbe_merge/schema/merge_datamodel.py

kg-microbe-core:
	poetry run kg merge -m duckdb -s "bacdive, mediadive, madin_etal, rhea_mappings, bactotraits, chebi, ec, envo, go, ncbitaxon, upa" --merge-label $@

kg-microbe-function:
	poetry run kg merge -m duckdb -n 1000000 -e 100000 -s "bacdive, mediadive, madin_etal, rhea_mappings, bactotraits, chebi, ec, envo, go, ncbitaxon, upa, uniprot_functional_microbes" --merge-label $@

kg-microbe-biomedical:
	poetry run kg merge -m duckdb -n 1000000 -e 100000 -s "bacdive, mediadive, madin_etal, rhea_mappings, bactotraits, ctd, wallen_etal, chebi, ec, envo, go, hp, mondo, ncbitaxon, upa, uniprot_human" --merge-label $@

kg-microbe-biomedical-function-merge:
	poetry run kg merge -m duckdb -n 1000000 -e 100000 -s "bacdive, mediadive, madin_etal, rhea_mappings, bactotraits, ctd, wallen_etal, chebi, ec, envo, go, hp, mondo, ncbitaxon, upa, uniprot_functional_microbes, uniprot_human" --merge-label $@