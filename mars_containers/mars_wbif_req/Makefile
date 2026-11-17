# Makefile for mars_WBIF_req, Web Browser InterFace agent, prototype

usage:
	@echo "make build, run, stop or rm"

build: Containerfile requirements.txt
	podman build -t mars_wbif_req:0.0 -f Containerfile

run:
	podman run -d --name=mars_wbif_req \
	 -e PYTHONUNBUFFERED=1 \
	 --network mars_network \
         --hostname=mars_wbif_req \
         -p 8002:8000 \
	 mars_wbif_req:0.0

stop:
	podman stop mars_wbif_req

rm:
	podman rm mars_wbif_req

logs:
	podman logs mars_wbif_req
