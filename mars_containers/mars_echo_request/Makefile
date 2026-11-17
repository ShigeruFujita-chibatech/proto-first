# Makefile for mars_agent_vanila

NAME=mars_echo_request



build: Containerfile
	podman build -t ${NAME}:0.0 -f Containerfile

run:
	podman run -d --name=${NAME} \
	-e PYTHONUNBUFFERED=1 \
         --hostname=${NAME} \
	 --network mars_network \
	 ${NAME}:0.0

stop:
	podman stop ${NAME}

rm:
	podman rm ${NAME}

logs:
	podman logs ${NAME}
