from Crawler import Crawler
from Email import Email
import os
from Logger import setup_logger
from dotenv import load_dotenv


class App:
    def __init__(self):
        load_dotenv()
        self._crawler = Crawler()
        self._email = Email()
        self._log = setup_logger(__name__)

    def run(self):
        self._log.info("Starting App...")
        soup = self._crawler.get_html_table()
        if self._do_send(soup):
            self._log.info("Sending Mail")
            self._email.send_mail(soup)
            self._log.info("Updating Previous Event Date.")
            with open("prev.txt", "w") as file:
                file.write(Crawler.get_current_event_date_str(soup))
        self._log.info("No new Events!")
        self._log.info("Done!")

    def _do_send(self, soup):
        self._log.info("Checking Events.")
        no_event_count = str(soup).count("Keine Vertretungen")
        self._log.info(f"No Event Count: {no_event_count}")
        if no_event_count == 2:
            return False
        return not Crawler.get_current_event_date_str(soup) == self._get_previous_event_date_str()

    def _get_previous_event_date_str(self):
        self._log.info("Retrieving previous event date info.")
        if os.path.isfile("./prev.txt"):
            with open("prev.txt", "r") as file:
                return file.read().strip()
        return ""


if __name__ == '__main__':
    app = App()
    app.run()
