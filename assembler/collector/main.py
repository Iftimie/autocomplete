from trie import Trie
import pickle
import logging
import falcon
import json


class Collector(object):

    def collect_phrase(self, phrase):
        with open("phrases.txt", 'a') as f:
            f.write(phrase+'\n')
        trie = Trie()
        with open("phrases.txt", 'r') as f:
            for line in f:
                trie.add_phrase(line)
        trie_local_file_name = "/app/assembler/collector/shared_data/trie.dat"
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


app = falcon.API()
app.add_route('/search', SearchResource())
