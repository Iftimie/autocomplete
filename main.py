import falcon
import json
import logging
import os
import pickle
from trie import Trie


class Collector(object):

    def collect_phrase(self, phrase):
        with open("phrases.txt", 'a') as f:
            f.write(phrase+'\n')
        trie = Trie()
        with open("phrases.txt", 'r') as f:
            for line in f:
                trie.add_phrase(line)
        trie_local_file_name = "trie.dat"
        pickle.dump(trie, open(trie_local_file_name, "wb"))


class SearchResource(object):
    def __init__(self):
        self._logger = logging.getLogger('gunicorn.error')
        self._collector = Collector()

    def on_post(self, req, resp):
        self._logger.debug(f'Handling request {req.url} with params {req.params}')

        try:
            self._collector.collect_phrase(req.params['phrase'])
            response_body = json.dumps(
                {
                    "status": "success",
                    "message": "Phrase sent for collection"
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


class Backend:
    def __init__(self):
        self._logger = logging.getLogger('gunicorn.error')

    def top_phrases_for_prefix(self, prefix):
        trie = self._load_trie()
        return trie.top_phrases_for_prefix(prefix)

    def _load_trie(self):
        trie_local_file_name = "trie.dat"
        if os.path.exists(trie_local_file_name):
            trie = pickle.load(open(trie_local_file_name, "rb"))
        else:
            trie = Trie()
        return trie
        

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


class Index(object):

    def on_get(self, req, resp):
        # do some sanity check on the filename
        resp.status = falcon.HTTP_200
        resp.content_type = 'text/html'
        with open('gateway/index.html', 'r') as f:
            resp.body = f.read()


app = falcon.API()

app.add_static_route('/static', os.path.join(os.path.dirname(__file__), "gateway"))

app.add_route('/search', SearchResource())

app.add_route('/top-phrases', TopPhrasesResource())

app.add_route('/', Index())
