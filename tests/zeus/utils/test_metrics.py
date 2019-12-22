from time import time
from zeus.utils.metrics import Counter, HitCounter, gauge


def test_hit_counter():
    current_ts = int(time())

    c = HitCounter(size=3)
    c.incr(current_ts=current_ts)
    c.incr(current_ts=current_ts)
    assert c.count(current_ts=current_ts) == 2
    assert c.count(1, current_ts=current_ts) == 2
    assert c.count(2, current_ts=current_ts) == 2

    current_ts += 1
    c.incr(current_ts=current_ts)
    assert c.count(current_ts=current_ts) == 3
    assert c.count(1, current_ts=current_ts) == 1
    assert c.count(2, current_ts=current_ts) == 3

    current_ts += 1
    c.incr(current_ts=current_ts)
    assert c.count(current_ts=current_ts) == 4
    assert c.count(1, current_ts=current_ts) == 1
    assert c.count(2, current_ts=current_ts) == 2

    current_ts += 1
    c.incr(current_ts=current_ts)
    assert c.count(current_ts=current_ts) == 3
    assert c.count(1, current_ts=current_ts) == 1
    assert c.count(2, current_ts=current_ts) == 2

    # dont incr here as it will force a truncate, and we just want to test
    # the fact that count skips invalid buckets
    current_ts += 1
    assert c.count(current_ts=current_ts) == 2
    assert c.count(1, current_ts=current_ts) == 0
    assert c.count(2, current_ts=current_ts) == 1

    current_ts += 1
    assert c.count(current_ts=current_ts) == 1
    assert c.count(1, current_ts=current_ts) == 0
    assert c.count(2, current_ts=current_ts) == 0

    current_ts += 1
    assert c.count(current_ts=current_ts) == 0
    assert c.count(1, current_ts=current_ts) == 0
    assert c.count(2, current_ts=current_ts) == 0


def test_gauge():
    counter = Counter()
    with gauge(counter):
        assert counter.value == 1
        with gauge(counter):
            assert counter.value == 2
        assert counter.value == 1
    assert counter.value == 0
