# Makefile for MARS

show:
	@echo "show_msg clean start clean_db"

clean:
	@echo "Clean MARS environment for developper"
	-podman stop mars_wbif
	-podman stop mars_ministral_3_14b_cit_cis_gpu0
	-podman stop mars_specialist
	-podman stop mars_orchestration
	podman rm -i mars_wbif
	podman rm -i mars_ministral_3_14b_cit_cis_gpu0
	podman rm -i mars_specialist
	podman rm -i mars_orchestration
	@echo "clean_database"
	make -C database clean_database

start:
	make -C orchestration build
	make -C orchestration run
	make -C mars_wbif build
	make -C mars_wbif run
	make -C mars_ministral_3_14b_cit_cis_gpu0 build
	make -C mars_ministral_3_14b_cit_cis_gpu0 run
	make -C mars_specialist build
	make -C mars_specialist run

full_start:
	make -C database run
	make start

clean_db:
	make -C database clean_database

show_msg:
	podman exec -it mars_database psql --username=mars_user -d mars_db -c "SELECT message_id,from_agent,to_agent,message->'content'->>'performative' AS performative FROM message_log ORDER BY message_id";

logs:
	podman logs mars_database

network_create:
	podman network create mars_network
