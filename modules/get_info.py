import time

from selenium.common import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from modules.load_django import *
from parser_app.models import Info


class MedCentersParser:

    BASE_URL = 'https://widget.nhsd.healthdirect.org.au/v1/widget/search?widgetId=9b5494f2-b4e6-495b-8d9c-e813dcebb7ca&types=%5Bservices_types%5D%3Ageneral+practice+service&delivery=PHYSICAL'

    def __init__(self):
        browser_options = ChromeOptions()
        service_args = [
            # '--headless',
            '--start-maximized',
            '--no-sandbox',
            '--disable-web-security',
            '--allow-running-insecure-content',
            '--hide-scrollbars',
            '--disable-setuid-sandbox',
            '--profile-directory=Default',
            '--ignore-ssl-errors=true',
            '--disable-dev-shm-usage',
        ]
        for arg in service_args:
            browser_options.add_argument(arg)

        browser_options.add_experimental_option(
            'excludeSwitches', ['enable-automation']
        )
        browser_options.add_experimental_option('prefs', {
            'profile.default_content_setting_values.notifications': 2,
            'profile.default_content_settings.popups': 0
        })

        self.driver = Chrome(options=browser_options)

    def placer_medcenter_parser(self):
        self.open_site()
        self.get_list_medcenters()

    def open_site(self):
        self.driver.get(self.BASE_URL)
        self._wait_and_choose_element('.ListItem__AppListItem-sc-1u2qtmw-0.mbJey')

    def get_list_medcenters(self):
        index = 1
        while True:
            try:
                element = self._wait_and_choose_element(
                    f'[class="ResultList__Container-sc-81kt74-0 cFqhkR"] li:nth-of-type({index})',
                    timeout=15,
                )
            except TimeoutException:
                break
            try:
                element.click()
            except ElementClickInterceptedException:
                continue
            time.sleep(1)
            try:
                self.get_info_single_medcenter_practitioner()
            except TimeoutException:
                continue

            index += 1

    def get_info_single_medcenter_practitioner(self):
        self._wait_and_choose_element('.ResultItem__Container-sc-1g9cevh-0.gdtonB')
        try:
            name = self._wait_and_choose_element('[class="ResultItem__Name-sc-1g9cevh-7 ceIVVX"]').text
        except TimeoutException:
            name = None
        try:
            address = self._wait_and_choose_element(
                '[class="ResultDetailSectionContent__DetailHeadline-s49pbx-1 dWJGdN"] + address'
            ).text.strip()
        except TimeoutException:
            address = None
        try:
            email = self.driver.find_element(
                By.XPATH,
                '//*[text()="Email: "]/a'
            ).text.strip()
        except NoSuchElementException:
            email = None
        try:
            fax = self.driver.find_element(
                By.XPATH,
                '//*[text()="Fax: "]'
            ).text.replace('Fax:', '').strip()
        except NoSuchElementException:
            fax = None
        try:
            website = self.driver.find_element(
                By.CSS_SELECTOR,
                '.dWJGdN + [class="ResultItem__CommsLink-sc-1g9cevh-23 heyebz"]'
            ).text.strip()
        except NoSuchElementException:
            website = None
        try:
            phone = self.driver.find_element(
                By.CSS_SELECTOR,
                '[class="ResultItem__CommsLink-sc-1g9cevh-23 heyebz"]'
            ).text.strip()
        except NoSuchElementException:
            phone = None
        try:
            practitioners = self.driver.find_elements(
                By.CSS_SELECTOR, '[class="ResultItem__PractitionerList-sc-1g9cevh-18 jkstcs"] li'
            )

        except NoSuchElementException:
            practitioners = None

        if not practitioners:
            defaults = {
                'address': address,
                'phone': phone,
                'email': email,
                'website': website,
                'fax': fax,
            }
            Info.objects.get_or_create(
                name=name,
                defaults=defaults,
            )

        for practitioner in practitioners:
            try:
                practitioner_name = practitioner.find_element(
                    By.CSS_SELECTOR,
                    '[class="ResultItem__PractionerName-sc-1g9cevh-19 hyVmse"]'
                ).text.strip()
            except NoSuchElementException:
                practitioner_name = None
            try:
                practitioner_profession = practitioner.find_element(
                    By.CSS_SELECTOR,
                    '[class="ResultItem__PractionerDetail-sc-1g9cevh-20 klkGoq"]:nth-of-type(2)'
                ).text.strip()
            except NoSuchElementException:
                practitioner_profession = None
            try:
                practitioner_sex = practitioner.find_element(
                    By.CSS_SELECTOR,
                    '[class="ResultItem__PractionerDetail-sc-1g9cevh-20 klkGoq"]:nth-of-type(3)'
                ).text.strip()
            except NoSuchElementException:
                practitioner_sex = None
            try:
                practitioner_lang = practitioner.find_element(
                    By.CSS_SELECTOR,
                    '[class="ResultItem__PractionerDetail-sc-1g9cevh-20 klkGoq"]:nth-of-type(4)'
                ).text.strip() or None
            except NoSuchElementException:
                practitioner_lang = None
            defaults = {
                'address': address,
                'phone': phone,
                'email': email,
                'fax': fax,
                'website': website,
                'practitioner_name': practitioner_name,
                'practitioner_profession': practitioner_profession,
                'practitioner_sex': practitioner_sex,
                'practitioner_lang': practitioner_lang,
            }

            Info.objects.get_or_create(
                name=name,
                practitioner_name=practitioner_name,
                defaults=defaults
            )

    def _wait_and_choose_element(self, selector: str, by: By = By.CSS_SELECTOR, timeout: int = 10) -> WebElement:
        condition = EC.presence_of_element_located((by, selector))
        element = WebDriverWait(self.driver, timeout).until(condition)
        return element

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.close()


if __name__ == '__main__':
    with MedCentersParser() as placer:
        placer.placer_medcenter_parser()
