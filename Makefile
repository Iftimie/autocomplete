DOCKER_NETWORK = autocomplete_default
ENV_FILE = assembler/hadoop/hadoop.env

run:
	sudo docker-compose up --scale distributor.backend=2
	# we have only two partitions. we start one distributor.backend for each partition

do_tasks:
	sudo docker build -t lopespm/tasks ./assembler/tasks
	sudo docker run \
	--network ${DOCKER_NETWORK} \
	--env-file ${ENV_FILE} \
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

populate_search:
	echo "Populating search phrases to the collector"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=awesome"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=ball"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=bank"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=car"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=car electric"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=dog"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=epsilon"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=far"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=furthest"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=games"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=games online"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=hello"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=hello world"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=irk"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=json"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=kangaroo animal"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=lars"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=make"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=mod"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=mod chip"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=modern style"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=nay"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=oat meal"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=quorum"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=quota"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=raspberry pi"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=saturn"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=turtles"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=union"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=vpn"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=wonderful"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=xbox"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=xtend"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=youtube music"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=zookeeper"
	curl -X POST -G http://localhost/search --data-urlencode "phrase=zk"

list:
	@grep '^[^#[:space:]].*:' Makefile

