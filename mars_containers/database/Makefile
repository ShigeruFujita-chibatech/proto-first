# Postgres for the Orchestration Agent

show_command:
	@echo "INFO: show_agents show_message show_message_log"
	@echo "DEV.: build run logs stop rm"
	@echo "DEV.: clean_database rm_database"

build:  Containerfile
	podman build -t mars_database:0.0 -f Containerfile

run:
	podman run -d --name=mars_database \
         -e PYTHONUNBUFFERED=1 \
         --hostname=mars_database \
         --network mars_network \
	 -e POSTGRES_USER=mars_user \
	 -e POSTGRES_PASSWORD=utc_cit_crs4_sec \
	 -e POSTGRES_DB=mars_db \
	 -v postgres_data:/var/lib/postgresql \
	 mars_database:0.0 

stop:
	podman stop mars_database

rm:
	podman rm mars_database

logs:
	podman logs mars_database

show_agents:
	@podman exec -it mars_database psql --username=mars_user -d mars_db -c "SELECT agent_name,agent_uuid,hostname,port_number,live_flag FROM agents ORDER BY agent_name;"

show_message:
	@podman exec -it mars_database psql --username=mars_user -d mars_db -c \
	   "SELECT message_id, \
                   from_agent, \
		   to_agent, \
		   message->'content'->>'performative' AS performative \
              FROM message_log ORDER BY message_id;"

show_message_log:
	@podman exec -it mars_database psql --username=mars_user -d mars_db -c "SELECT * FROM message_log ORDER BY message_id;"

show_tables:
	@podman exec -it mars_database psql --username=mars_user -d mars_db -c "SELECT tablename FROM pg_tables;"

rm_database:
	podman volume rm postgres_data

clean_database:
	podman exec -it mars_database psql --username=mars_user -d mars_db -c "DELETE FROM message_log;"
	podman exec -it mars_database psql --username=mars_user -d mars_db -c "DELETE FROM agents;"
