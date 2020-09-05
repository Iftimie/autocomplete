import falcon
import json
import logging
import os
import pickle
from trie import Trie


class Backend:
    def __init__(self):
        self._logger = logging.getLogger('gunicorn.error')
        self.trie = Trie()

    def top_phrases_for_prefix(self, prefix):
        return self.trie.top_phrases_for_prefix(prefix)

    def _load_trie(self, trie_file):
        shared_path = "/app/distributor/backend/shared_data"
        self.trie = pickle.load( open(os.path.join(shared_path, trie_file), "rb"))


class TopPhrasesResource(object):
    def __init__(self, backend):
        self._logger = logging.getLogger('gunicorn.error')
        self._backend = backend

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


class ReloadTrieResource(object):
    def __init__(self, backend):
        self._logger = logging.getLogger('gunicorn.error')
        self._backend = backend

    def on_post(self, req, resp):
        self._logger.debug(f'Handling {req.method} request {req.url} with params {req.params}')
        try:
            trie_file = req.params['trie_file']
            self._backend._load_trie(trie_file)
            response_body = json.dumps(
                {
                    "status": "success",
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
common_backend = Backend()
top_phrases_resource = TopPhrasesResource(common_backend)
app.add_route('/top-phrases', top_phrases_resource)

reload_trie_resource = ReloadTrieResource(common_backend)
app.add_route('/reload-trie', reload_trie_resource)


