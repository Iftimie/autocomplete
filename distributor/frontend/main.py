import falcon
import json
import logging
import os
import requests
import random
import logging
import pickle
from distutils.util import strtobool
from kazoo.client import KazooClient, DataWatch

ZK_NEXT_TARGET = '/phrases/distributor/next_target'

class BackendNodesNotAvailable(Exception):
	pass

class Frontend:

	def __init__(self):
		self._logger = logging.getLogger('gunicorn.error')
		self._zk = KazooClient(hosts=f'{os.getenv("ZOOKEEPER_HOST")}:2181')

	def start(self):
		self._zk.start()

	def stop(self):
		self._zk.stop()		

	# Using Cache Aside Pattern
	def top_phrases_for_prefix(self, prefix):
		
		backend_hostname = self.backend_for_prefix(prefix)

		if (backend_hostname is None):
			raise BackendNodesNotAvailable("No backend nodes available to complete the request")

		self._logger.debug(f'Getting phrases from host {backend_hostname}')
		r = requests.get(f'http://{backend_hostname}:6000/top-phrases', params = {'prefix': prefix})
		self._logger.debug(f'request content: {r.content}; r.json(): {r.json()}')
		top_phrases = r.json()["data"]["top_phrases"]

		return top_phrases

	def backend_for_prefix(self, prefix):

		if (self._zk.exists(ZK_NEXT_TARGET) is None):
			return None

		target_id = self._zk.get(ZK_NEXT_TARGET)[0].decode()
		if (not target_id):
			return None

		partitions = self._zk.get_children(f'/phrases/distributor/{target_id}/partitions')
		for partition in partitions:
			start, end = partition.split('|')
			if ((not start or prefix >= start) and (not end or prefix < end)):

				node_path = f'/phrases/distributor/{target_id}/partitions/{partition}'

				hostname = self._zk.get(node_path)[0].decode()

				return hostname

		return None

class MainResource(object):
	def __init__(self):
		self._logger = logging.getLogger('gunicorn.error')
		self._frontend = Frontend()
		self._frontend.start()

	def on_get(self, req, resp):
		self._logger.debug(f'Handling {req.method} request {req.url} with params {req.params}')
		try:
			top_phrases = self._frontend.top_phrases_for_prefix(req.params['prefix'])
			response_body = json.dumps(
				{
					"status": "success",
					"data": {
						"top_phrases": top_phrases 
					}
				 })
			resp.status = falcon.HTTP_200
			resp.body = response_body
			
		except BackendNodesNotAvailable as err:
			response_body = json.dumps(
				{
					"status": "error",
					"message": "No backend nodes available to complete the request"
				 })
			resp.status = falcon.HTTP_500
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
main_resource = MainResource()
app.add_route('/top-phrases', main_resource)