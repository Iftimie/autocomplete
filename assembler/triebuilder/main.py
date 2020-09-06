from trie import Trie
import pickle
import logging
import os
import time
from kazoo.client import KazooClient, DataWatch
import shutil

SHARED_PATH = "/app/assembler/triebuilder/shared_targets/"
SHARED_TRIES = "/app/assembler/triebuilder/shared_tries/"
ZK_ASSEMBLER_LAST_BUILT_TARGET = '/phrases/assembler/last_built_target'
ZK_NEXT_TARGET = '/phrases/distributor/next_target'


class TrieBuilder:
    def __init__(self):
        self._zk = KazooClient(hosts=f'{os.getenv("ZOOKEEPER_HOST")}:2181')
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.getLevelName(os.getenv("LOG_LEVEL", "INFO")))
        ch = logging.StreamHandler()
        ch.setLevel(logging.getLevelName(os.getenv("LOG_LEVEL", "INFO")))
        self._logger.addHandler(ch)

    def start(self):
        self._zk.start()
        datawatch_next_target = DataWatch(client=self._zk, path=ZK_ASSEMBLER_LAST_BUILT_TARGET, func=self._on_assembler_last_built_target_changed)

    def stop(self):
        self._zk.stop()

    def _on_assembler_last_built_target_changed(self, data, stat, event=None):
        self._logger.debug("_on_assembler_last_built_target_changed Data is %s" % data)
        if (data is None):
            return

        self.build(data.decode())

    def _is_already_built(self, target_id):
        if self._zk.exists(ZK_NEXT_TARGET) is None:
            return False
        next_target_id = self._zk.get(ZK_NEXT_TARGET)[0].decode()
        return next_target_id == target_id

    def build(self, target_id):
        if not target_id or self._is_already_built(target_id):
            return False

        try:

            self._logger.info(f"target_id {target_id}, SHARED_PATH {SHARED_PATH}")

            trie = self._create_trie(target_id)

            trie_local_file_name = "trie.dat"
            pickle.dump(trie, open(trie_local_file_name, "wb"))

            shared_path = os.path.join(SHARED_TRIES, f"trie_{target_id}.dat")
            shutil.copyfile(trie_local_file_name, shared_path)

            self._register_next_target_zookeeper(target_id)
        except Exception as e:
            self._logger.error("Error while building tree"+str(e))

    def _create_trie(self, target_id):
        trie = Trie()
        target_dir = SHARED_PATH + target_id
        for file in os.listdir(target_dir):
            with open(os.path.join(target_dir, file), "r") as f:
                for phrase in f.readlines():
                    trie.add_phrase(phrase)
        return trie

    def _register_next_target_zookeeper(self, target_id):
        base_zk_path = ZK_NEXT_TARGET
        self._zk.ensure_path(f'{base_zk_path}')
        self._zk.set(f'{base_zk_path}', target_id.encode())


if __name__ == '__main__':
    trie_builder = TrieBuilder()
    trie_builder.start()
    print("Trie builder started")
    while True:
        time.sleep(5)