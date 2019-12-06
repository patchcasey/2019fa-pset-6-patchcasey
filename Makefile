.PHONY: data 46a4bb62

HASH_ID:
	46a4bb62

data:
	data/yelp_subset_*

data/yelp_subset_*:
    aws s3 cp s3://cscie29-data/46a4bb62/pset_5/yelp_data/ data/ --recursive --exclude "*" --include "yelp_subset_*" --request-payer=requester