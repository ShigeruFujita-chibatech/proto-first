# Makefile for mars_specialist, prototype

NAME=mars_specialist

usage:
	@echo "make build, run, stop or rm"

build: Containerfile requirements.txt 
	podman build -t ${NAME}:0.0 -f Containerfile

run:
	podman run -d --name=${NAME} \
	 -e PYTHONUNBUFFERED=1 \
	 --network mars_network \
         --hostname=${NAME} \
	 ${NAME}:0.0

stop:
	podman stop ${NAME}

rm:
	podman rm ${NAME}

logs:
	podman logs ${NAME}
