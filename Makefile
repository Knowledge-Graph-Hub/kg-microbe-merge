datamodel:
	poetry run gen-python kg_microbe_merge/schema/merge_schema.yaml > kg_microbe_merge/schema/merge_datamodel.py

kg-microbe-core: datamodel
	poetry run kg merge -m duckdb -s "bacdive, mediadive, madin_etal, rhea_mappings, bactotraits, chebi, ec, envo, go, ncbitaxon, upa" --merge-label $@
	poetry run python kg_microbe_merge/utils/edge_vs_node_check.py $@
	@# If missing nodes were found, add them to the nodes file
	@if [ -f data/merged/$@/$@_missing_nodes_with_category.tsv ]; then \
		cd data/merged/$@ && \
		mv merged-kg_nodes.tsv merged-kg_nodes_part.tsv && \
		cat merged-kg_nodes_part.tsv $@_missing_nodes_with_category.tsv > merged-kg_nodes.tsv && \
		rm $@_missing_nodes.tsv $@_missing_nodes_with_category.tsv merged-kg_nodes_part.tsv; \
	fi

kg-microbe-function: datamodel
	poetry run kg merge -m duckdb -s "bacdive, mediadive, madin_etal, rhea_mappings, bactotraits, chebi, ec, envo, go, ncbitaxon, upa, uniprot_functional_microbes" --merge-label $@
	poetry run python kg_microbe_merge/utils/edge_vs_node_check.py $@
	@# If missing nodes were found, add them to the nodes file
	@if [ -f data/merged/$@/$@_missing_nodes_with_category.tsv ]; then \
		cd data/merged/$@ && \
		mv merged-kg_nodes.tsv merged-kg_nodes_part.tsv && \
		cat merged-kg_nodes_part.tsv $@_missing_nodes_with_category.tsv > merged-kg_nodes.tsv && \
		rm $@_missing_nodes.tsv $@_missing_nodes_with_category.tsv merged-kg_nodes_part.tsv; \
	fi

kg-microbe-biomedical: datamodel
	poetry run kg merge -m duckdb -s "bacdive, mediadive, madin_etal, rhea_mappings, bactotraits, chebi, ec, envo, go, ncbitaxon, upa, hp, mondo, disbiome, ctd, wallen_etal, uniprot_human" --merge-label $@
	poetry run python kg_microbe_merge/utils/edge_vs_node_check.py $@
	@# If missing nodes were found, add them to the nodes file
	@if [ -f data/merged/$@/$@_missing_nodes_with_category.tsv ]; then \
		cd data/merged/$@ && \
		mv merged-kg_nodes.tsv merged-kg_nodes_part.tsv && \
		cat merged-kg_nodes_part.tsv $@_missing_nodes_with_category.tsv > merged-kg_nodes.tsv && \
		rm $@_missing_nodes.tsv $@_missing_nodes_with_category.tsv merged-kg_nodes_part.tsv; \
	fi

kg-microbe-biomedical-function: datamodel
	poetry run kg merge -m duckdb --merge-label $@
	poetry run python kg_microbe_merge/utils/edge_vs_node_check.py $@
	@# If missing nodes were found, add them to the nodes file
	@if [ -f data/merged/$@/$@_missing_nodes_with_category.tsv ]; then \
		cd data/merged/$@ && \
		mv merged-kg_nodes.tsv merged-kg_nodes_part.tsv && \
		cat merged-kg_nodes_part.tsv $@_missing_nodes_with_category.tsv > merged-kg_nodes.tsv && \
		rm $@_missing_nodes.tsv $@_missing_nodes_with_category.tsv merged-kg_nodes_part.tsv; \
	fi

kg-microbe-function-cat:
	@# Check that kg-microbe-core exists
	@if [ ! -f data/merged/kg-microbe-core/merged-kg_nodes.tsv ]; then \
		echo "Error: kg-microbe-core must be built first. Run 'make kg-microbe-core' first."; \
		exit 1; \
	fi
	cd data/raw/uniprot_functional_microbes && \
	grep UniprotKB: nodes.tsv > nodes_UniprotKB.tsv && \
	tail -n +2 edges.tsv | cut -f1,2,3 > edges_data_clean.tsv && \
	head -1 edges.tsv | cut -f1,2,3 > edges_header_clean.tsv && \
	cd ../../merged && \
	mkdir -p kg-microbe-function-cat && \
	cd kg-microbe-core && \
	tail -n +2 merged-kg_edges.tsv > edges_data.tsv && \
	head -1 merged-kg_edges.tsv > edges_header.tsv && \
	cd ../ && \
	cd kg-microbe-function-cat && \
	cat ../kg-microbe-core/merged-kg_nodes.tsv ../../raw/uniprot_functional_microbes/nodes_UniprotKB.tsv > merged-kg_nodes.tsv && \
	cat ../kg-microbe-core/edges_header.tsv ../kg-microbe-core/edges_data.tsv ../../raw/uniprot_functional_microbes/edges_data_clean.tsv > merged-kg_edges.tsv
	poetry run python kg_microbe_merge/utils/edge_vs_node_check.py kg-microbe-function-cat
	@# If missing nodes were found, add them to the nodes file
	@if [ -f data/merged/kg-microbe-function-cat/kg-microbe-function-cat_missing_nodes_with_category.tsv ]; then \
		cd data/merged/kg-microbe-function-cat && \
		mv merged-kg_nodes.tsv merged-kg_nodes_part.tsv && \
		cat merged-kg_nodes_part.tsv kg-microbe-function-cat_missing_nodes_with_category.tsv > merged-kg_nodes.tsv && \
		rm kg-microbe-function-cat_missing_nodes.tsv kg-microbe-function-cat_missing_nodes_with_category.tsv merged-kg_nodes_part.tsv; \
	fi

kg-microbe-biomedical-function-cat:
	@# Check that kg-microbe-biomedical exists
	@if [ ! -f data/merged/kg-microbe-biomedical/merged-kg_nodes.tsv ]; then \
		echo "Error: kg-microbe-biomedical must be built first. Run 'make kg-microbe-biomedical' first."; \
		exit 1; \
	fi
	cd data/raw/uniprot_functional_microbes && \
	grep UniprotKB: nodes.tsv > nodes_UniprotKB.tsv && \
	tail -n +2 edges.tsv | cut -f1,2,3 > edges_data_clean.tsv && \
	head -1 edges.tsv | cut -f1,2,3 > edges_header_clean.tsv && \
	cd ../../merged && \
	cd kg-microbe-biomedical && \
	tail -n +2 merged-kg_edges.tsv > edges_data.tsv && \
	head -1 merged-kg_edges.tsv > edges_header.tsv && \
	cd ../ && \
	mkdir -p kg-microbe-biomedical-function-cat && \
	cd kg-microbe-biomedical-function-cat && \
	cat ../kg-microbe-biomedical/merged-kg_nodes.tsv ../../raw/uniprot_functional_microbes/nodes_UniprotKB.tsv > merged-kg_nodes.tsv && \
	cat ../kg-microbe-biomedical/edges_header.tsv ../kg-microbe-biomedical/edges_data.tsv ../../raw/uniprot_functional_microbes/edges_data_clean.tsv > merged-kg_edges.tsv
	poetry run python kg_microbe_merge/utils/edge_vs_node_check.py kg-microbe-biomedical-function-cat
	@# If missing nodes were found, add them to the nodes file
	@if [ -f data/merged/kg-microbe-biomedical-function-cat/kg-microbe-biomedical-function-cat_missing_nodes_with_category.tsv ]; then \
		cd data/merged/kg-microbe-biomedical-function-cat && \
		mv merged-kg_nodes.tsv merged-kg_nodes_part.tsv && \
		cat merged-kg_nodes_part.tsv kg-microbe-biomedical-function-cat_missing_nodes_with_category.tsv > merged-kg_nodes.tsv && \
		rm kg-microbe-biomedical-function-cat_missing_nodes.tsv kg-microbe-biomedical-function-cat_missing_nodes_with_category.tsv merged-kg_nodes_part.tsv; \
	fi

clean:
	# Remove generated datamodel
	rm -f kg_microbe_merge/schema/merge_datamodel.py

	# Remove all merged directories
	rm -rf data/merged/kg-microbe-core
	rm -rf data/merged/kg-microbe-function
	rm -rf data/merged/kg-microbe-function-cat
	rm -rf data/merged/kg-microbe-biomedical
	rm -rf data/merged/kg-microbe-biomedical-function
	rm -rf data/merged/kg-microbe-biomedical-function-cat

	# Remove temporary files created during concatenation
	rm -f data/raw/uniprot_functional_microbes/nodes_UniprotKB.tsv
	rm -f data/raw/uniprot_functional_microbes/edges_data_clean.tsv
	rm -f data/raw/uniprot_functional_microbes/edges_header_clean.tsv

	# Remove any edge_data and edge_header files in merged directories
	find data/merged -name "edges_data.tsv" -type f -delete 2>/dev/null || true
	find data/merged -name "edges_header.tsv" -type f -delete 2>/dev/null || true

	@echo "Cleaned all generated files"

include kg-microbe-merge.Makefile

