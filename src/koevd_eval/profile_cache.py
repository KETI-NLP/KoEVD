"""Bounded, disposable numerical cache; never an authority for publication.

Only application-selected numerical projections enter this cache. Current
publication and recovery checks must happen outside it on every request.
"""
from collections import OrderedDict
from concurrent.futures import Future
import json
from threading import Lock

from .results import canonical_hash
from .storage import encode


VERSION = 'koevd-public-numerical-profile-v1'
FIELDS = ('format', 'artifact_sha256', 'protocol', 'scoring', 'statistics',
          'interpretation', 'tasks', 'task3_task5', 'quality', 'signal_thresholds',
          'signals', 'charts')


def numerical_profile(profile):
    """Whitelist analytical output; omit originals, cases and source identities."""
    value = {key: profile[key] for key in FIELDS}
    disagreement = profile['measurement_disagreement']
    value['measurement_disagreement'] = {
        key: disagreement[key] for key in ('count', 'comparable_sources', 'interpretation')}
    # Round trip also detaches every nested object from the analysis engine.
    return json.loads(encode(value))


class NumericalProfileCache:
    def __init__(self, *, max_entries=128, max_bytes=64 * 1024**2):
        if (type(max_entries) is not int or max_entries < 1
                or type(max_bytes) is not int or max_bytes < 1):
            raise ValueError('Positive numerical cache bounds required')
        self.max_entries, self.max_bytes = max_entries, max_bytes
        self._entries, self._pending = OrderedDict(), {}
        self._size, self._lock = 0, Lock()

    def get_or_compute(self, identity, compute):
        key = canonical_hash({'projection': VERSION, **identity})
        with self._lock:
            if key in self._entries:
                self._entries.move_to_end(key)
                return json.loads(self._entries[key])
            future = self._pending.get(key)
            leader = future is None
            if leader:
                future = self._pending[key] = Future()
        if not leader:
            return json.loads(future.result())
        try:
            blob = encode(compute())
            with self._lock:
                if len(blob) <= self.max_bytes:
                    while self._entries and (len(self._entries) >= self.max_entries
                                              or self._size + len(blob) > self.max_bytes):
                        _, removed = self._entries.popitem(last=False)
                        self._size -= len(removed)
                    self._entries[key] = blob
                    self._size += len(blob)
                self._pending.pop(key)
                future.set_result(blob)
            return json.loads(blob)
        except BaseException as exc:
            with self._lock:
                self._pending.pop(key, None)
                future.set_exception(exc)
            raise
