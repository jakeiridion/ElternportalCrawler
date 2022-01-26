import sys
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
        try:
            soup = self._get_soup()
        except requests.exceptions.ConnectionError as e:
            self._log.error(f"Can not connect to Elternportal. Check EP_URL in .env file. - {e}")
            sys.exit(1)
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

    def _get_csrf_token(self, r):
        soup = BeautifulSoup(r.content, "html.parser")
        return soup.find("input", attrs={"name": "csrf"})["value"]

    def _login(self, csrf_token, session):
        self._log.info("Logging into Elternportal...")
        payload = {
            "username": os.getenv("EP_USERNAME"),
            "password": os.getenv("EP_PASSWORD"),
            "csrf": csrf_token,
            "go_to": ""
        }
        r = session.post(self._login_url, data=payload)
        self._check_login(r.url)

    def _check_login(self, url):
        if self._login_is_successful(url):
            self._log.info("Login successful.")
        else:
            self._log.error("Login Error! - Check EP_USERNAME/EP_PASSWORD in .env file.")
            sys.exit(1)

    def _login_is_successful(self, url):
        return url.endswith("/start")

    @staticmethod
    def get_current_event_date_str(soup):
        return soup.find("div", attrs={"class": "list full_width"}).text
