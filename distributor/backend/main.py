import falcon
import json
import logging
import os
import pickle
from trie import Trie
from kazoo.client import KazooClient, DataWatch
from hdfs import InsecureClient
from docker import Client  # to find the scaled container ID
import os
import socket


ZK_NEXT_TARGET = '/phrases/distributor/next_target'
min_lexicographic_char = chr(0)
max_lexicographic_char = chr(255)
HOSTNAME = os.environ.get("HOSTNAME")
NUMBER_NODES_PER_PARTITION = 1


class HdfsClient:
    def __init__(self, namenode_host):
        self._client = InsecureClient(f'http://{namenode_host}:9870')

    def download(self, remote_hdfs_path, local_path):
        self._client.download(remote_hdfs_path, local_path, overwrite=True)


class Backend:
    def __init__(self):
        self._logger = logging.getLogger('gunicorn.error')
        self._trie = Trie()
        self._zk = KazooClient(hosts=f'{os.getenv("ZOOKEEPER_HOST")}:2181')
        self._hdfsClient = HdfsClient(os.getenv("HADOOP_NAMENODE_HOST"))
        self.partition_index = self.find_self_partition()

    def find_self_partition(self):
        cli = Client(base_url='unix://var/run/docker.sock')
        all_containers = cli.containers()
        # filter out ourself by HOSTNAME
        our_container = [c for c in all_containers if c['Id'][:12] == HOSTNAME[:12]][0]
        return int(our_container['Names'][0].split('_')[-1]) - 1
        

    def start(self):
        self._zk.start()
        datawatch_next_target = DataWatch(client=self._zk, path=ZK_NEXT_TARGET, func=self._on_next_target_changed)

    def _on_next_target_changed(self, data, stat, event=None):
        self._logger.info("_on_next_target_changed Data is %s" % data)
        if (data is None or data == b''):
            return
        next_target_id = data.decode()

        next_target_id = self._zk.get(ZK_NEXT_TARGET)[0].decode()
        self._attempt_to_join_target(next_target_id)

    def _attempt_to_join_target(self, target_id):
        if (not target_id or self._zk.exists(f'/phrases/distributor/{target_id}') is None):
            return
        partitions = self._zk.get_children(f'/phrases/distributor/{target_id}/partitions')
        partition = partitions[self.partition_index]

        node_path = f'/phrases/distributor/{target_id}/partitions/{partition}'
        self._zk.set(node_path, socket.gethostname().encode())

        trie_data_hdfs_path = f'/phrases/distributor/{target_id}/partitions/{partition}/trie_data_hdfs_path'
        self._trie = self._load_trie(self._zk.get(trie_data_hdfs_path)[0].decode())

    def stop(self):
        self._zk.stop()

    def top_phrases_for_prefix(self, prefix):
        return self._trie.top_phrases_for_prefix(prefix)

    def _load_trie(self, trie_hdfs_path):
        local_path = 'trie.dat'
        self._hdfsClient.download(trie_hdfs_path, local_path)
        return pickle.load( open(local_path, "rb"))

class TopPhrasesResource(object):
    def __init__(self):
        self._logger = logging.getLogger('gunicorn.error')
        self._backend = Backend()
        self._backend.start()

    def on_get(self, req, resp):
        self._logger.debug(f'Handling {req.method} request {req.url} with params {req.params}')
        try:
            top_phrases = self._backend.top_phrases_for_prefix(req.params['prefix'])
            response_body = json.dumps(
                {
                    "status": "success",
                    "data": {
                        "top_phrases": top_phrases 
                    }
                    })
            resp.status = falcon.HTTP_200
            resp.body = response_body

        except Exception as e:
            self._logger.error('An error occurred when processing the request', exc_info=e)
            response_body = json.dumps(
                {
                    "status": "error",
                    "message": "An error occurred when processing the request"
                    })
            resp.status = falcon.HTTP_500
            resp.body = response_body


app = falcon.API()
app.add_route('/top-phrases', TopPhrasesResource())
