# Orchestration Agent

default:
	@echo 'mars orchestration agent'
	@echo 'make run, It will wait for connection http://localhost:8001/'
	@echo build run stop rm logs

build: Containerfile
	podman build -t mars_orchestration:0.0 -f Containerfile

run:
	podman run -d --name=mars_orchestration \
         -e PYTHONUNBUFFERED=1 \
	 --network mars_network \
         --hostname=mars_orchestration \
         -p 8001:8001 \
	 mars_orchestration:0.0
	@echo 'wait for connection http://localhost:8001/'

stop:
	podman stop mars_orchestration

rm:
	podman rm mars_orchestration

logs:
	podman logs mars_orchestration
