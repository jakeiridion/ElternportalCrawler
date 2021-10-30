import requests
from bs4 import BeautifulSoup
import os
from Logger import setup_logger
from urllib.parse import urljoin


class Crawler:
    def __init__(self):
        self._url = os.getenv("EP_URL")
        self._login_url = urljoin(self._url, "includes/project/auth/login.php")
        self._service_url = urljoin(self._url, "service/vertretungsplan")
        self._headers = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/5320 (KHTML, like Gecko) "
                          "Chrome/37.0.837.0 Mobile Safari/5320 "
        }
        self._log = setup_logger(__name__)

    def get_html_table(self):
        soup = self._get_soup()
        self._log.info("Retrieving Table...")
        return soup.find("div", attrs={"class": "main_center"})

    def _get_soup(self):
        with requests.session() as session:
            session.headers = self._headers
            r = session.get(self._url)
            csrf_token = self._get_csrf_token(r)
            self._login(csrf_token, session)
            r = session.get(self._service_url)
            return BeautifulSoup(r.text, "html.parser")

    def _login(self, csrf_token, session):
        self._log.info("Logging into Elternportal...")
        payload = {
            "username": os.getenv("EP_USERNAME"),
            "password": os.getenv("EP_PASSWORD"),
            "csrf": csrf_token,
            "go_to": ""
        }
        session.post(self._login_url, data=payload)

    def _get_csrf_token(self, r):
        soup = BeautifulSoup(r.content, "html.parser")
        return soup.find("input", attrs={"name": "csrf"})["value"]

    @staticmethod
    def get_current_event_date_str(soup):
        return soup.find("div", attrs={"class": "list full_width"}).text

