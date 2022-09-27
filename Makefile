.PHONY: clean clean_data data env_create lint test testwatch enable_hooks sync_data_to_s3 sync_data_from_s3


#################################################################################
# DOC                                                                           #
#################################################################################
#
# Make's special variables:
#   $@ is the target
#   $^ is all prereqs
#   $< is the first prereq
#   $* is the "stem" of the "pattern rule" match


#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
S3_BUCKET = [OPTIONAL] your-bucket-for-syncing-data (do not include 's3://')
AWS_PROFILE = default
PROJECT_NAME = shellhackathon


#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Make data
data:
	python shellhackathon/data/make_dataset.py data/raw data/interim

## Delete all compiled Python files
clean:
	find . -name "*.pyc" -exec rm {} \;

## Delete all data
clean_data:
	rm -rf data/interim/*
	rm -rf data/processed/*

## Create dependency visualization from Makefile
dep.png: Makefile
	python bin/makefile2dot.py < Makefile | dot -Tpng > dep.png
	open dep.png

## Set up an environment with pipenv
env_create:
	pipenv install numpy scipy pandas matplotlib seaborn jupyter nbstripout sklearn mypy flake8 pytest pytest-watch click click_log

## Lint using flake8 and mypy
lint:
	flake8 shellhackathon
	mypy shellhackathon

## Run the unit tests
test:
	pytest

## Run tests on every file change
testwatch:
	ptw

## Enable flake8 and nbstripout hooks
enable_hooks:
	# flake8
	flake8 --install-hook=git
	git config --bool flake8.strict true
	# nbstripout
	nbstripout --install --attributes .gitattributes

## Upload Data to S3
sync_data_to_s3:
ifeq (default,$(AWS_PROFILE))
	aws s3 sync data/ s3://$(S3_BUCKET)/data/
else
	aws s3 sync data/ s3://$(S3_BUCKET)/data/ --profile $(AWS_PROFILE)
endif

## Download Data from S3
sync_data_from_s3:
ifeq (default,$(AWS_PROFILE))
	aws s3 sync s3://$(S3_BUCKET)/data/ data/
else
	aws s3 sync s3://$(S3_BUCKET)/data/ data/ --profile $(AWS_PROFILE)
endif


#################################################################################
# PROJECT RULES                                                                 #
#################################################################################



#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := show-help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: show-help
show-help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
