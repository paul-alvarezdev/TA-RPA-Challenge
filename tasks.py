from robocorp.tasks import task
from nytimes_scrapper import NYTimesScrapper 
import os

@task
def main():
    os.environ['DISPLAY'] = ':0'
    nys = NYTimesScrapper()
    nys.get_fresh_news()


if __name__ == "__main__":
    main()