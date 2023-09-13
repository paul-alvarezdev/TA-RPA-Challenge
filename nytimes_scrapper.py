from selenium.common.exceptions import ElementNotInteractableException, ElementClickInterceptedException
from selenium.webdriver.remote.webelement import WebElement
from SeleniumLibrary.errors import ElementNotFound
from dateutil.relativedelta import relativedelta
from RPA.Browser.Selenium import Selenium
from config_manager import ConfigManager
from excel_manager import ExcelManager
from RPA.FileSystem import FileSystem
from typing import Tuple, Optional
from datetime import date
from robocorp import log
import requests
import time
import re
import os

class NYTimesScrapper:
    
    browser_lib = Selenium()
    browser_aux = Selenium()
    excel = ExcelManager()
    file = FileSystem()
    news_list = {
        "title": [],
        "date": [],
        "description": [],
        "picture_filename": [],
        "phrase_count": [],
        "contains_money": [],
    }

    def __init__(self) -> None:
        # Create output folder
        self.setup_output_folder()

    def setup_output_folder(self):
        """ Creates output fodler if not exists
        If exists deletes all contents
        """
        output_dir = os.path.join('.', 'output')
        if self.file.does_directory_exist(output_dir):
            for dir_file in self.file.list_files_in_directory(output_dir):
                self.file.remove_file(dir_file[0])
        else:
            self.file.create_directory(output_dir)
    
    def replace_phrase_in_url(self) -> str:
        """ Returns the base url
        Replaces the auxiliar [search_phrase] with the SEARCH_PHRASE constant from the config_manager.py file.
        """
        url = ConfigManager.BASE_URL.replace('[search_phrase]', ConfigManager.SEARCH_PHRASE)
        return url
    
    def calculate_daterange(self) -> Tuple[str, str]:
        """ Returns the start_date and end_date.
        Calculates the dates based on today's date and the MONTHS_NUMBER from the config_manager.py file
        If the MONTHS_NUMBER input equals 0 is replaced to 1 to ensure both 0 an 1 can work to subtract 1 month from today's date
        """
        today = date.today()
        months_number = ConfigManager.MONTHS_NUMBER
        if not months_number: months_number = 1
        start_date = (today - relativedelta(months=months_number)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        return start_date, end_date

    def replace_daterange_in_url(self, url: str) -> str:
        """ Returns the site url
        Replaces the auxiliar [end_date] in the url with the calculated end_date.
        Replaces the auxiliar [start_date] in the url with the calculated start_date.
        """
        start_date, end_date = self.calculate_daterange()
        url = url.replace('[end_date]', end_date)
        url = url.replace('[start_date]', start_date)
        return url
    
    def replace_sections_in_url(self, url: str) -> str:
        """ Returns the site url
        Embbeds all the input sections in the base url by replacing the auxiliar %2C[sections] with the corresponding section code.
        The section codes are extracted from the NYTimes site and are constants in the config manager file.
        This means new sections should be coded to work but the efficiency and robustness increases.
        """
        auxiliar = '%2C[sections]'
        for section in enumerate(ConfigManager.SECTIONS):
            url = url.replace(auxiliar, ConfigManager.SECTION_CODES[section[1]] + auxiliar)
        url = url.replace(auxiliar, '')
        return url

    def open_website(self, url: str):
        """ Opens browser based on the input URL.
        The browser window is maximized.
        """
        self.browser_lib.open_available_browser(url, maximized=True)
        
    def close_popup_window(self):
        """ Closes the popup window "We've updated our terms".
        If popup window is still hidden the bot will attempt to close it again before waiting 1 second.
        If popup window was not closed before 30 attempts an error is thrown.
        """
        attempts = 30
        for i in range(attempts):
            try:
                continue_button_locator = 'xpath: //*[contains(text(), "Continue")]'
                self.browser_lib.click_element(continue_button_locator)
                break
            except (ElementNotInteractableException, ElementNotFound):
                if i == attempts:
                    raise Exception('Unable to locate the popup window: We\'ve updated our terms')
                time.sleep(1)   # Wait 1 second to allow popup window to load

    def show_all_news(self):
        """ Clicks in the 'SHOW MORE' button of the search page to load all the available news
        It will stop once the 'SHOW MORE' button disappears.
        """
        time.sleep(2)   # Avoid Target Adds
        show_more_button_locator = 'css: [data-testid="search-show-more-button"]'
        while True:
            try:
                self.browser_lib.click_element(show_more_button_locator)
                time.sleep(2)   # Allow news to load
            except (ElementNotFound, ElementClickInterceptedException):
                break # End of the news reached
            
    def get_article_date(self, article: WebElement) -> str:
        """ Returns the Date of the current article by looking for the data-testid property
        """
        date_locator = 'span[data-testid="todays-date"]'
        date = article.find_element("css selector", date_locator).text
        return date
    
    def get_article_title(self, article: WebElement) -> str:
        """ Returns the Title of the current article by looking for the <h4> tag
        """
        title_locator = 'div div div a h4'
        title = article.find_element("css selector", title_locator).text
        return title
    
    def get_article_description(self, article: WebElement) -> Optional[str]:
        """ Returns the Description of the current article by looking for the <p> tag
        If the locator is not found, the description is not available
        If the locator finds the word 'By' at the begginning of the element text, the description is not available
        If the description is not available the function returns None
        """
        try:
            description_locator = 'div div div a p'
            description = article.find_element('css selector', description_locator).text
            if description_locator.split(' ')[0].strip() == 'By': return None
            return description
        except ElementNotFound:
            return None
    
    def get_article_picture_url(self, article: WebElement) -> Optional[str]:
        """ Returns the picture url of the current article by looking for the <img> tag
        """
        try:
            picture_locator = 'figure div img'
            picture_url = article.find_element('css selector', picture_locator).get_property('src')
            return picture_url
        except ElementNotFound:
            return None
        
    def get_article_picture_filename(self, picture_url: str) -> str:
        """ Returns the picture filename of the current article by clenaing the base img url
        """
        if picture_url is None:
            return
        picture_filename = picture_url.split('/')[-1]
        picture_filename = picture_filename.split('?quality')[0]
        return picture_filename
    
    def download_article_picture(self, picture_url: str, picture_filename: str):
        """ Downloads the article picture if available based on an input url
        """
        if picture_url is None:
            return
        # Set picture name
        output_folder = os.path.join(os.getcwd(), 'output')
        output_path = os.path.join(output_folder, picture_filename)
        response = requests.get(picture_url)
        # Download
        if response.status_code:
            fp = open(output_path, 'wb')
            fp.write(response.content)
            fp.close() 

    def count_phrase_occurrences(self, search_phrase: str, article_text: str) -> int:
        """ counts the amount of occurrences of the search phrase in the article text
        Both search phrase and article text are converted to lowercase for better analysis
        """
        phrase_count = article_text.lower().count(search_phrase.lower())
        return phrase_count
    
    def check_if_article_has_money(self, article_text: str) -> bool:
        """ Returns True or False depending if the article text contains money amounts
        The search is not case sensitive
        """
        dollar_sign_format = r'\$\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?'
        word_dollars_format = r'\b\d+\s+dollars\b'
        currency_code_format = r'\b\d+\s+USD\b'
        pattern = '|'.join([dollar_sign_format, word_dollars_format, currency_code_format])
        if re.search(pattern, article_text, re.IGNORECASE):
            return True
        return False

    def get_news_list(self):
        """ Retrieves the news
        """
        # Get news
        # news_table_locator = 'xpath: //*[@data-testid="search-bodega-result"]'
        news_table_locator = 'css: li[data-testid="search-bodega-result"]'
        news_table = self.browser_lib.find_elements(news_table_locator)

        for article in news_table:
            date = self.get_article_date(article) # Extract article date

            title = self.get_article_title(article) # Extract article title

            description = self.get_article_description(article) # Extract article description

            picture_url = self.get_article_picture_url(article) # Extract picture url

            picture_filename = self.get_article_picture_filename(picture_url)   # Extract picture filename

            self.download_article_picture(picture_url, picture_filename)    # Download picture 
            
            article_text = f'{title} {description}' # Join title + description

            phrase_count = self.count_phrase_occurrences(ConfigManager.SEARCH_PHRASE, article_text) # Count search phrase ocurrences

            article_has_money = self.check_if_article_has_money(article_text) # Check if article contains any amount of money

            # Store article data
            self.news_list["title"].append(title)
            self.news_list["date"].append(date)
            self.news_list["description"].append(description)
            self.news_list["picture_filename"].append(picture_filename)
            self.news_list["phrase_count"].append(phrase_count)
            self.news_list["contains_money"].append(article_has_money)

    def get_fresh_news(self):
        """ Main function responsible for function call management, download pictures.
        """
        # The next methods replace the input parameters in the base URL. (from the config_manager.py)
        # The objective is perform the search and set the filters through the url (filters: date range, sections and relevance).
        # This allow us to acheive a more robust automation by skipping steps.
        # The relevance filter is already embedded in the base url. (to sort news by the newest)
        url = self.replace_phrase_in_url()
        url = self.replace_daterange_in_url(url)
        url = self.replace_sections_in_url(url)

        log.console_message(url)
        
        self.open_website(url)
        time.sleep(2)
        self.close_popup_window()
        time.sleep(2)
        # Click on show more button to display all news
        self.show_all_news()

        # Retrieve all news from the NYTimes search website
        self.get_news_list()

        # Store news in excel file
        self.excel.write_in_excel_file(self.news_list)

