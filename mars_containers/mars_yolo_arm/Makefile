# Makefile for mars_agent_vanila

build: Containerfile
	podman build -t mars_yolo_arm:0.0 -f Containerfile

run:
	podman run -d --name=mars_yolo_arm \
	-e PYTHONUNBUFFERED=1 \
         --hostname=mars_yolo_arm \
	 --network mars_network \
	 mars_yolo_arm:0.0

stop:
	podman stop mars_yolo_arm

rm:
	podman rm mars_yolo_arm

logs:
	podman logs mars_yolo_arm
