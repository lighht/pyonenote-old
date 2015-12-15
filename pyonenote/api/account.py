import time


class Account:
    def __init__(self, session_info, expires_at=None):
        if expires_at is None:
            expires_at = time.time() + session_info['expires_in']
        self.expires_at = expires_at
        print(expires_at)
