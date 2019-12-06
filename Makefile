.PHONY: data

data:
	aws s3 cp s3://cscie29-data/46a4bb62/pset_5/yelp_data/ data/ --recursive --exclude "*" --include "yelp_subset_*" --request-payer=requester