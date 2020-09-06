import falcon
import json
import logging
import os
import pickle
from trie import Trie
from kazoo.client import KazooClient, DataWatch

ZK_NEXT_TARGET = '/phrases/distributor/next_target'

class Backend:
    def __init__(self):
        self._logger = logging.getLogger('gunicorn.error')
        self._trie = Trie()
        self._zk = KazooClient(hosts=f'{os.getenv("ZOOKEEPER_HOST")}:2181')

    def start(self):
        self._zk.start()
        datawatch_next_target = DataWatch(client=self._zk, path=ZK_NEXT_TARGET, func=self._on_next_target_changed)

    def _on_next_target_changed(self, data, stat, event=None):
        self._logger.info("_on_next_target_changed Data is %s" % data)
        if (data is None or data==b''):
            return
        next_target_id = data.decode()
        self._load_trie(next_target_id)

    def stop(self):
        self._zk.stop()

    def top_phrases_for_prefix(self, prefix):
        return self._trie.top_phrases_for_prefix(prefix)

    def _load_trie(self, target_id):
        shared_path = "/app/distributor/backend/shared_tries"
        trie_path = os.path.join(shared_path, f"trie_{target_id}.dat")
        if os.path.exists(trie_path):
            self._trie = pickle.load(open(trie_path,'rb'))
        else:
            self._logger.warning(f"File does not exist {trie_path}")


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
