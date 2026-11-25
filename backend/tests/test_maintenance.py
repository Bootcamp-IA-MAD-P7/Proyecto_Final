import json
import logging
import threading

from app.logs import JsonFormatter
from app.maintenance import Maintenance


def test_runs_a_cycle_each_interval_until_stopped(caplog):
    maintenance = Maintenance()
    stop = threading.Event()
    original = maintenance.run_cycle

    def cycle():
        original()
        if maintenance.cycles == 3:
            stop.set()

    maintenance.run_cycle = cycle

    with caplog.at_level(logging.INFO, logger="app.maintenance"):
        thread = threading.Thread(target=maintenance.run, args=(stop, 0.01))
        thread.start()
        thread.join(timeout=5)

    assert not thread.is_alive()
    events = [record.message for record in caplog.records]
    assert events[0] == "maintenance ready"
    assert events.count("maintenance cycle completed") == 3
    assert events[-1] == "maintenance stopped"


def test_a_cycle_is_logged_as_a_json_line():
    record = logging.LogRecord("app.maintenance", logging.INFO, __file__, 1, "cycle", None, None)
    record.count = 2

    entry = json.loads(JsonFormatter("maintenance").format(record))

    assert entry["process"] == "maintenance"
    assert entry["event"] == "cycle"
    assert entry["count"] == 2
    assert entry["level"] == "info"
