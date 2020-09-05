import falcon
import json
import logging
import os
import pickle
from trie import Trie


class Backend:
    def __init__(self):
        self._logger = logging.getLogger('gunicorn.error')
        self.trie = None
        self.trie_file = None

    def top_phrases_for_prefix(self, prefix):
        self._load_trie()
        return trie.top_phrases_for_prefix(prefix)

    def _load_trie(self):
        shared_path = "/app/distributor/backend/shared_data"
        trie_files = sorted(os.listdir(shared_path))
        if trie_files and trie_files[-1]!=self.trie_file:
            self.trie = pickle.load( open(os.path.join(shared_path, trie_files[-1]), "rb"))
            self.trie_file = trie_files[-1]
        else:
            self.trie = Trie()
        

class TopPhrasesResource(object):
    def __init__(self):
        self._logger = logging.getLogger('gunicorn.error')
        self._backend = Backend()

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

