import smtplib
import ssl
import re
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from Crawler import Crawler
from Logger import setup_logger
from socket import gaierror


class Email:
    def __init__(self):
        self._log = setup_logger(__name__)
        self._smtp_server = os.getenv("SMTP_SERVER")
        self._smtp_server_port = 465
        self._username = os.getenv("EMAIL_ADDRESS")
        self._password = os.getenv("EMAIL_PASSWORD")
        self._receivers = self._get_receivers()
        if not self._receivers:
            self._log.info("No Emails listed in receivers.txt")
            sys.exit(0)

    def _get_receivers(self):
        with open("receivers.txt", "r") as file:
            return [line.strip() for line in file.readlines() if not line.startswith("#")]

    def send_mail(self, soup):
        context = ssl.create_default_context()
        try:
            with smtplib.SMTP_SSL(self._smtp_server, self._smtp_server_port, context=context) as server:
                self._log.info("Logging into SMTP Server.")
                server.login(self._username, self._password)
                self._log.info("Sending Mail.")
                server.sendmail(self._username, self._receivers, self._create_message(soup).as_string())
        except smtplib.SMTPAuthenticationError as e:
            self._log.error(f"SMTP Credentials are invalid. Check EMAIL_ADDRESS/EMAIL_PASSWORD in .env file. - {e}")
            sys.exit(1)
        except gaierror as e:
            self._log.error(f"SMTP Server address is invalid. Check SMTP_SERVER in .env file. - {e}")
            sys.exit(1)
        except UnicodeEncodeError as e:
            self._log.error(f"No Special Characters in SMTP Login Credentials."
                            f"Check EMAIL_ADDRESS/EMAIL_PASSWORD in .env file. - {e}")
            sys.exit(1)

    def _create_message(self, soup):
        message = MIMEMultipart("alternative")
        message["Subject"] = self._get_subject(soup)
        message["From"] = self._username
        message["Bcc"] = ", ".join(self._receivers)
        part = MIMEText(soup, "html")
        message.attach(part)
        return message

    def _get_subject(self, soup):
        date_str = Crawler.get_current_event_date_str(soup)
        date_str, time_str = re.match(r"Stand:\s([\d.]+)\s([\d:]+)", date_str).groups()
        return f"Vertretungsplan {date_str}-{time_str}"
