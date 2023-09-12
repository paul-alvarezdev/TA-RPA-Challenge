from RPA.Browser.Selenium import Selenium
from nytimes_scrapper import NYTimesScrapper 

def main():
    nys = NYTimesScrapper()
    nys.get_fresh_news()


if __name__ == "__main__":
    main()