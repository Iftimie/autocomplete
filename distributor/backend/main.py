import falcon
import json
import logging
import os
import pickle
from trie import Trie
from kazoo.client import KazooClient, DataWatch
from hdfs import InsecureClient

ZK_NEXT_TARGET = '/phrases/distributor/next_target'
min_lexicographic_char = chr(0)
max_lexicographic_char = chr(255)


class HdfsClient:
    def __init__(self, namenode_host):
        self._client = InsecureClient(f'http://{namenode_host}:9870')

    def download(self, remote_hdfs_path, local_path):
        self._client.download(remote_hdfs_path, local_path, overwrite=True)


class Backend:
    def __init__(self):
        self._logger = logging.getLogger('gunicorn.error')
        self._tries = [(Trie(), min_lexicographic_char, max_lexicographic_char)]
        self._zk = KazooClient(hosts=f'{os.getenv("ZOOKEEPER_HOST")}:2181')
        self._hdfsClient = HdfsClient(os.getenv("HADOOP_NAMENODE_HOST"))


    def start(self):
        self._zk.start()
        datawatch_next_target = DataWatch(client=self._zk, path=ZK_NEXT_TARGET, func=self._on_next_target_changed)

    def _on_next_target_changed(self, data, stat, event=None):
        self._logger.info("_on_next_target_changed Data is %s" % data)
        if (data is None or data == b''):
            return
        next_target_id = data.decode()

        partitions = self._zk.get_children(f'/phrases/distributor/{next_target_id}/partitions')
        self._tries = []
        for partition in partitions:
            trie_data_hdfs_path = f'/phrases/distributor/{next_target_id}/partitions/{partition}/trie_data_hdfs_path'
            trie = self._load_trie(self._zk.get(trie_data_hdfs_path)[0].decode())
            start, end = partition.split('|')
            if not start: start = min_lexicographic_char
            if not end: end = max_lexicographic_char
            self._tries.append((trie, start, end))


    def stop(self):
        self._zk.stop()

    def top_phrases_for_prefix(self, prefix):
        for trie, start, end in self._tries:
            if start <= prefix < end:
                return trie.top_phrases_for_prefix(prefix)

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
