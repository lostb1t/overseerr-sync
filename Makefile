build:
	docker build -t ghcr.io/lostb1t/overseersync:latest .

push:
	docker push ghcr.io/lostb1t/overseersync:latest

deploy:
	nomad job run nomad.hcl

release: build push deploy