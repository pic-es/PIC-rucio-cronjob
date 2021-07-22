IMAGE := bruzzese/test

test_1:
	python json-validator.py --load_json ../rucio-sync-rses/docker/config/rse_repository.json
test_2:
	python json-validator.py --load_json ../rucio-sync-clients/docker/config/account_repository.json

image:
	docker build -t $(IMAGE) .

push-image:
	docker push $(IMAGE)


.PHONY: image push-image test

