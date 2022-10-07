import uuid
from datetime import datetime
from pathlib import Path

from cir_sniper.config import BASE_URL, REQUEST_SESSION_DATA_DIRECTORY, REQUEST_SESSION_KEEP
from cir_sniper.loggerfactory import LoggerFactory

import requests
from tenacity import retry, wait_fixed, stop_after_attempt

logger = LoggerFactory.get_logger("sniper.session")


class SniperSession:
    def __init__(self):
        self.session = requests.Session()
        # self.session.headers["User-Agent"] = ""  # TODO set user-agent
        # Setup directory to save session responses
        now = datetime.now()
        self.session_data_path = Path(REQUEST_SESSION_DATA_DIRECTORY) / now.strftime("%Y-%m-%dT%H:%M:%S")
        if REQUEST_SESSION_KEEP:
            self.session_data_path.mkdir(parents=True, exist_ok=True)

    @property
    def cookies(self):
        return self.session.cookies

    @retry(reraise=True, stop=stop_after_attempt(3), wait=wait_fixed(1))
    def _request(self, method: str, url: str, **kwargs):
        request_id = uuid.uuid4()
        logger.debug(f"{request_id}: {method} {url} {kwargs}")
        resp = self.session.request(method=method, url=url, **kwargs)
        logger.debug(f"{request_id} complete")
        try:
            resp.raise_for_status()
        except:
            pass
        finally:
            if REQUEST_SESSION_KEEP:
                cleaned_url = url.replace(BASE_URL, '').replace('/', '_')
                respFile = self.session_data_path / f"{method}__{cleaned_url}__{request_id}.html"
                respFile.write_text(resp.text)
        return resp

    def get(self, url: str, **kwargs):
        return self._request(method="get", url=url, **kwargs)

    def post(self, url: str, **kwargs):
        return self._request(method="post", url=url, **kwargs)

    def update_cookies(self, cookie_jar):
        self.session.cookies.update(requests.utils.dict_from_cookiejar(cookie_jar))

    def close(self):
        self.session.close()
