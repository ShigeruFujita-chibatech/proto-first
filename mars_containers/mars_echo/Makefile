# Makefile for mars_echo

build: Containerfile
	podman build -t mars_echo:0.0 -f Containerfile

run:
	podman run -d --name=mars_echo \
	-e PYTHONUNBUFFERED=1 \
         --hostname=mars_echo \
	 --network mars_network \
	 mars_echo:0.0

stop:
	podman stop mars_echo

rm:
	podman rm mars_echo

logs:
	podman logs mars_echo
