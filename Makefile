DOCKER_NETWORK = autocomplete_default

run:
	sudo docker-compose up

do_tasks:
	sudo docker build -t lopespm/tasks ./assembler/tasks
	sudo docker run \
	--network ${DOCKER_NETWORK} \
	-v "$$(pwd)/shared/shared_phrases":"/app/assembler/tasks/shared_phrases" \
	-v "$$(pwd)/shared/shared_targets":"/app/assembler/tasks/shared_targets" \
	lopespm/tasks

setup:

	while [ "$$(echo "stat" | nc localhost 2181 | grep Mode)" != "Mode: standalone" ] ; do \
	    echo "Waiting for zookeeper to come online" ; \
	    sleep 2 ; \
	done

	sudo docker exec zookeeper ./bin/zkCli.sh -server localhost:2181 create /phrases ""
	sudo docker exec zookeeper ./bin/zkCli.sh -server localhost:2181 create /phrases/assembler ""
	sudo docker exec zookeeper ./bin/zkCli.sh -server localhost:2181 create /phrases/assembler/last_built_target ""

	sudo docker exec zookeeper ./bin/zkCli.sh -server localhost:2181 create /phrases/distributor ""
	sudo docker exec zookeeper ./bin/zkCli.sh -server localhost:2181 create /phrases/distributor/current_target ""
	sudo docker exec zookeeper ./bin/zkCli.sh -server localhost:2181 create /phrases/distributor/next_target ""

clean:
	sudo rm -Rf shared/
	mkdir shared
	mkdir shared/shared_data
	mkdir shared/shared_phrases
	mkdir shared/shared_targets
	git checkout HEAD -- shared/trie.py