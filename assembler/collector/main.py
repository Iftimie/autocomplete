import logging
import os
import falcon
import json
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer


key_schema_str = """
{
   "namespace": "io.github.lopespm.autocomplete.phrases",
   "name": "key",
   "type": "record",
   "fields" : [
     { "name" : "phrase", "type" : "string" }
   ]
}
"""

value_schema_str = """
{
   "namespace": "io.github.lopespm.autocomplete.phrases",
   "name": "value",
   "type": "record",
   "fields" : [
     { "name" : "phrase", "type" : "string" }
   ]
}
"""


class Collector(object):

    def __init__(self):
        value_schema = avro.loads(value_schema_str)
        key_schema = avro.loads(key_schema_str)
        self._producer = AvroProducer({
            'bootstrap.servers': f'{os.getenv("BROKER_HOST")}:9092',
            'schema.registry.url': f'http://{os.getenv("SCHEMA_REGISTRY_HOST")}:8081',
            'on_delivery': self._delivery_report
            }, default_key_schema=key_schema, default_value_schema=value_schema)
        self._logger = logging.getLogger('gunicorn.info')

    def _delivery_report(self, err, msg):
        """ Called once for each message produced to indicate delivery result. Triggered by poll() or flush(). """
        if err is not None:
            self._logger.error('Message delivery to broker failed: {}'.format(err))
        else:
            self._logger.info('Message delivered to broker on {} [{}]'.format(msg.topic(), msg.partition()))

    def collect_phrase(self, phrase):
        self._producer.produce(topic='phrases', value={"phrase": phrase}, key={"phrase": phrase})
        self._producer.flush()


class SearchResource(object):
    def __init__(self):
        self._logger = logging.getLogger('gunicorn.debug')
        self._collector = Collector()

    def on_post(self, req, resp):
        self._logger.info(f'Handling request {req.url} with params {req.params}')
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
