# Makefile for mars_WBIF, Web Browser InterFace agent, prototype

NAME=mars_wbif

usage:
	@echo "make build, run, stop or rm"

build: Containerfile requirements.txt app/${NAME}.py
	podman build -t ${NAME}:0.0 -f Containerfile

run:
	echo "You can access to wbif from http://127.0.0.1:8002/ from web-browser"
	podman run -d --name=${NAME} \
	 -e PYTHONUNBUFFERED=1 \
	 --network mars_network \
         --hostname=${NAME} \
         -p 8002:8001 \
	 ${NAME}:0.0

stop:
	podman stop ${NAME}

rm:
	podman rm ${NAME}

logs:
	podman logs ${NAME}

clean:
	-podman stop ${NAME}
	podman rm -i ${NAME}
