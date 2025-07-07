from datetime import datetime, timedelta
from collections import defaultdict
from threading import Lock

class RateLimiter:
    def __init__(self, limit: int, interval_sec: int):
        self.limit = limit
        self.interval = timedelta(seconds=interval_sec)
        self.access_times = defaultdict(list)
        self.lock = Lock()

    def is_allowed(self, ip: str) -> bool:
        with self.lock:
            now = datetime.now()
            access_list = [t for t in self.access_times[ip] if now - t < self.interval]
            self.access_times[ip] = access_list

            if len(access_list) < self.limit:
                self.access_times[ip].append(now)
                return True
            return False

limiter = RateLimiter(limit=5, interval_sec=60)