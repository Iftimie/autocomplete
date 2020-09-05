import logging
import os
import falcon
import json
import time
import requests


class Collector(object):

    def collect_phrase(self, phrase):
        shared_path = "/app/assembler/collector/shared_phrases"
        sorted_files = sorted(os.listdir(shared_path))
        current_time = time.time()
        seconds_30 = 30
        if not sorted_files:
            curfile = str(int(current_time))
        elif int(sorted_files[-1])+seconds_30 < current_time:
            curfile = str(int(current_time))
            requests.post(f"http://assembler.triebuilder:4000/build_trie?phrase_file={int(sorted_files[-1])}")
        else:       
            curfile = sorted_files[-1]
        fullpath = os.path.join(shared_path, curfile)

        with open(fullpath, 'a') as f:
            f.write(phrase+'\n')


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
