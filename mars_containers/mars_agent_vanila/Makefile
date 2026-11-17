# Makefile for mars_agent_vanila

build: Containerfile
	podman build -t mars_vanila:0.0 -f Containerfile

run:
	podman run -d --name=mars_vanila \
	 --network mars_network \
         --hostname=mars_vanila \
         -p 8000:8000 \
	 mars_vanila:0.0

stop:
	podman stop mars_vanila

rm:
	podman rm mars_vanila

logs:
	podman logs mars_vanila
