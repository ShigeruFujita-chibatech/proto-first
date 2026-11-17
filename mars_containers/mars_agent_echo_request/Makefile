# Makefile for mars_agent_vanila

build: Containerfile
	podman build -t mars_vanila_agent_echo_request:0.0 -f Containerfile

run:
	podman run -d --name=mars_vanila_agent_echo_request \
	-e PYTHONUNBUFFERED=1 \
         --hostname=mars_vanila_agent_echo_request \
	 --network mars_network \
	 mars_vanila_agent_echo_request:0.0

stop:
	podman stop mars_vanila_agent_echo_request

rm:
	podman rm mars_vanila_agent_echo_request

logs:
	podman logs mars_vanila_agent_echo_request
