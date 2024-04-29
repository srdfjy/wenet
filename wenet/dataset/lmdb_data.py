import io
import random
import pickle

import lmdb
import torchaudio


class LmdbData:

    def __init__(self, lmdb_file):
        self.db = lmdb.open(lmdb_file,
                            readonly=True,
                            lock=False,
                            readahead=False)
        with self.db.begin(write=False) as txn:
            obj = txn.get(b'__keys__')
            assert obj is not None
            self.keys = pickle.loads(obj)
            assert isinstance(self.keys, list)

    def random_one(self):
        assert len(self.keys) > 0
        index = random.randint(0, len(self.keys) - 1)
        key = self.keys[index]
        with self.db.begin(write=False) as txn:
            value = txn.get(key.encode())
            assert value is not None
        return key, value

    def check(self):
        for key in self.keys:
            with self.db.begin(write=False) as txn:
                value = txn.get(key.encode())
                info = torchaudio.info(io.BytesIO(value))
                # print(key, info)
                # if info.num_channels != 1 or info.sample_rate != 8000 or info.bits_per_sample != 16:
                if info.num_channels != 1 or info.bits_per_sample != 16:
                    print(key, info)

    def __del__(self):
        self.db.close()
