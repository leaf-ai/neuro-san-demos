import logging
import threading
import time

from apps.message_bus import MessageBus


class FakePubSubWorkerThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self._stop_event = threading.Event()

    def run(self):
        while not self._stop_event.is_set():
            time.sleep(0.01)

    def stop(self):
        self._stop_event.set()


class FakePubSub:
    def __init__(self):
        self.callback = None

    def subscribe(self, **kwargs):
        # store the callback
        self.callback = next(iter(kwargs.values()))

    def run_in_thread(self, sleep_time=0.001, daemon=True):
        thread = FakePubSubWorkerThread()
        thread.daemon = daemon
        thread.start()
        self.thread = thread
        return thread

    def publish_message(self, data):
        if self.callback:
            self.callback({"data": data})


class FakeRedis:
    def __init__(self):
        self.pubsub_instance = FakePubSub()

    @classmethod
    def from_url(cls, url):
        return cls()

    def pubsub(self):
        return self.pubsub_instance

    def publish(self, topic, data):
        self.pubsub_instance.publish_message(data)


def _patch_redis(monkeypatch):
    fake_redis = FakeRedis()
    monkeypatch.setattr("apps.message_bus.redis.Redis.from_url", lambda url: fake_redis)
    return fake_redis


def test_subscribe_and_unsubscribe(monkeypatch):
    fake_redis = _patch_redis(monkeypatch)
    bus = MessageBus()
    thread = bus.subscribe("test", lambda msg: None)
    assert thread.is_alive()
    bus.unsubscribe(thread)
    assert not thread.is_alive()


def test_logs_malformed_message(monkeypatch, caplog):
    fake_redis = _patch_redis(monkeypatch)
    bus = MessageBus()
    bus.subscribe("test", lambda msg: None)
    with caplog.at_level(logging.WARNING):
        fake_redis.pubsub_instance.publish_message(b"not json")
    assert any("Malformed message" in record.message for record in caplog.records)
