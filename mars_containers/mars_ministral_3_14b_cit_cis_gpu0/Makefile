# Makefile for mars_WBIF, Web Browser InterFace agent, prototype

NAME=mars_ministral_3_14b_cit_cis_gpu0

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
