from trie import Trie
import pickle
import logging
import os
import falcon
import json


class BuildTrie(object):
    def __init__(self):
        self._logger = logging.getLogger('gunicorn.info')

    def on_post(self, req, resp):
        self._logger.info(f'Handling request {req.url}')

        try:
            phrase_file = req.params['phrase_file']
            shared_path = "/app/assembler/triebuilder/shared_phrases"

            trie = Trie()
            for phrase_file in sorted(os.listdir(shared_path)):
                fullpath = os.path.join(shared_path, phrase_file)
                with open(fullpath, 'r') as f:
                    for line in f:
                        trie.add_phrase(line)
            trie_local_file_name = f"/app/assembler/triebuilder/shared_data/trie_{phrase_file}.dat"
            pickle.dump(trie, open(trie_local_file_name, "wb"))

            response_body = json.dumps(
                {
                    "status": "success",
                    "message": "Trie built"
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
app.add_route('/build_trie', BuildTrie())
