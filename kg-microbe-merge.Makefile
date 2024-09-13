# This Makefile is used to automate the process of creating releases and tags for the kg-microbe-merge repository.
# It includes commands to check and split large tarball files, create GitHub releases, and tag commits.
#
# Commands:
# - release: Creates a new release on GitHub after checking and splitting large tarball files if necessary.
# - pre-release: Creates a new pre-release on GitHub after checking and splitting large tarball files if necessary.
# - tag: Creates a new tag on GitHub after checking and splitting large tarball files if necessary.
# - check-and-split: Checks if tarball files are larger than 2GB and splits them if needed.
#
# Examples:
# - To create a new release:
#   make release
#
# - To create a new pre-release:
#   make pre-release
#
# - To create a new tag:
#   make tag

# Define variables
REPO_OWNER := Knowledge-Graph-Hub
REPO_NAME := kg-microbe-merge
REPO_URL := https://github.com/$(REPO_OWNER)/$(REPO_NAME)
TOKEN := $(GH_TOKEN)
TAR_GZ_FILES := $(shell find data/merged -type f -name '*.tar.gz')
PART_SIZE := 2000M  # Size of each part (less than 2GB)

.PHONY: release pre-release tag check-and-split

release: check-and-split
	$(call create_release,release)

pre-release: check-and-split
	$(call create_release,pre-release)

tag: check-and-split
	$(call create_tag)

check-and-split:
	@for tarball in $(TAR_GZ_FILES); do \
		if [ $$(stat -c%s "$$tarball") -gt 2147483648 ]; then \
			echo "$$tarball is larger than 2GB. Tarballing individual files..."; \
			dir=$$(dirname $$tarball); \
			for file in nodes.tsv edges.tsv; do \
				if [ -f "$$dir/$$file" ]; then \
					tarball_name=$$(basename $$dir)_$$file.tar.gz; \
					tar -czvf $$tarball_name -C $$dir $$file; \
					echo "Tarball generated successfully as $$tarball_name."; \
				else \
					echo "$$dir/$$file does not exist. Skipping."; \
				fi \
			done; \
		else \
			echo "$$tarball is less than 2GB. No need to split."; \
		fi \
	done

define create_release
	@echo "Creating a $(1) on GitHub..."
	@read -p "Enter $(1) tag (e.g., $(shell date +%Y-%m-%d)): " TAG_NAME; \
	read -p "Enter $(1) title: " RELEASE_TITLE; \
	read -p "Enter $(1) notes: " RELEASE_NOTES; \
	if git rev-parse "$$TAG_NAME" >/dev/null 2>&1; then \
		echo "Error: Tag '$$TAG_NAME' already exists. Please choose a different tag."; \
		exit 1; \
	fi; \
	git tag -a $$TAG_NAME -m "$$RELEASE_TITLE"; \
	git push origin $$TAG_NAME; \
	gh release create $$TAG_NAME --title "$$RELEASE_TITLE" --notes "$$RELEASE_NOTES" $(if $(filter $(1),pre-release),--prerelease) --repo $(REPO_OWNER)/$(REPO_NAME); \
	for tarball in $(TAR_GZ_FILES); do \
		gh release upload $$TAG_NAME $$tarball --repo $(REPO_OWNER)/$(REPO_NAME); \
	done; \
	echo "$(capitalize $(1)) $$TAG_NAME created successfully."
endef

define create_tag
	@echo "Creating a release on GitHub..."
	@read -p "Enter release tag (e.g., $(shell date +%Y-%m-%d)): " TAG; \
	read -p "Enter release title: " RELEASE_TITLE; \
	read -p "Enter release notes: " RELEASE_NOTES; \
	git tag -a $$TAG -m "$$RELEASE_TITLE"; \
	git push origin $$TAG; \
	for tarball in $(TAR_GZ_FILES); do \
		gh release upload $$TAG $$tarball --repo $(REPO_OWNER)/$(REPO_NAME); \
	done; \
	echo "Release $$TAG created successfully."
endef

capitalize = $(subst $(1),$(shell echo $(1) | tr '[:lower:]' '[:upper:]'),$(1))
