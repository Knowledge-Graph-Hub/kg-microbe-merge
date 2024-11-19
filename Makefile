datamodel:
	poetry run gen-python kg_microbe_merge/schema/merge_schema.yaml > kg_microbe_merge/schema/merge_datamodel.py

kg-microbe-core:
	poetry run kg merge -m duckdb -s "bacdive, mediadive, madin_etal, rhea_mappings, bactotraits, chebi, ec, envo, go, ncbitaxon, upa" --merge-label $@

kg-microbe-function:
	poetry run kg merge -m duckdb -s "bacdive, mediadive, madin_etal, rhea_mappings, bactotraits, chebi, ec, envo, go, ncbitaxon, upa, uniprot_functional_microbes" --merge-label $@

kg-microbe-biomedical:
	poetry run kg merge -m duckdb -s "bacdive, mediadive, madin_etal, rhea_mappings, bactotraits, chebi, ec, envo, go, ncbitaxon, upa, hp, mondo, disbiome, ctd, wallen_etal, uniprot_human" --merge-label $@

kg-microbe-biomedical-function:
	poetry run kg merge -m duckdb --merge-label $@

kg-microbe-function-cat:
	cd data/raw/uniprot_functional_microbes && \
	grep UniprotKB: nodes.tsv > nodes_UniprotKB.tsv && \
	tail -n +2 edges.tsv | cut -f1,2,3 > edges_data_clean.tsv && \
	head -1 edges.tsv | cut -f1,2,3 > edges_header_clean.tsv && \
	cd ../../merged && \
	mkdir -p kg-microbe-function-cat && \
	cd kg-microbe-core && \
	tail -n +2 edges.tsv > edges_data.tsv && \
	cd ../ && \
	cd kg-microbe-function-cat && \
	cat ../kg-microbe-core/nodes.tsv ../../raw/uniprot_functional_microbes/nodes_UniprotKB.tsv ../kg-microbe-core/kg-microbe-core_missing_nodes_with_category.tsv > merged-kg_nodes.tsv && \
	cat ../kg-microbe-core/edges_header.tsv ../kg-microbe-core/edges_data.tsv ../../raw/uniprot_functional_microbes/edges_data_clean.tsv > merged-kg_edges.tsv && \
	cd ../../../ && \
	poetry run python kg_microbe_merge/utils/edge_vs_node_check.py kg-microbe-function-cat && \
	cd data/merged/kg-microbe-function-cat && \
	mv merged-kg_nodes.tsv merged-kg_nodes_part.tsv  && \
	cat merged-kg_nodes_part.tsv kg-microbe-function-cat_missing_nodes_with_category.tsv > merged-kg_nodes.tsv  && \
	cd ../../../

kg-microbe-biomedical-function-cat:
	
	cd data/raw/uniprot_functional_microbes && \
	grep UniprotKB: nodes.tsv > nodes_UniprotKB.tsv && \
	tail -n +2 edges.tsv | cut -f1,2,3 > edges_data_clean.tsv && \
	head -1 edges.tsv | cut -f1,2,3 > edges_header_clean.tsv && \
	cd ../../merged && \
	cd kg-microbe-biomedical && \
	tail -n +2 edges.tsv > edges_data.tsv && \
	cd ../ && \
	mkdir -p kg-microbe-biomedical-function-cat && \
	cd kg-microbe-biomedical-function-cat && \
	cat ../kg-microbe-biomedical/nodes.tsv ../../raw/uniprot_functional_microbes/nodes_UniprotKB.tsv > merged-kg_nodes.tsv ../kg-microbe-biomedical/kg-microbe-biomedical_missing_nodes_with_category.tsv && \
	cat ../kg-microbe-core/edges_header.tsv ../kg-microbe-biomedical/edges_data.tsv ../../raw/uniprot_functional_microbes/edges_data_clean.tsv > merged-kg_edges.tsv && \
	cd ../../../ && \
	poetry run python kg_microbe_merge/utils/edge_vs_node_check.py kg-microbe-biomedical-function-cat && \
	cd data/merged/kg-microbe-biomedical-function-cat && \
	mv merged-kg_nodes.tsv merged-kg_nodes_part.tsv  && \
	cat merged-kg_nodes_part.tsv kg-microbe-biomedical-function-cat_missing_nodes_with_category.tsv > merged-kg_nodes.tsv  && \
	cd ../../../

include kg-microbe-merge.Makefile

