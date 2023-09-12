from robocorp.tasks import task
from nytimes_scrapper import NYTimesScrapper 

@task
def main():
    nys = NYTimesScrapper()
    nys.get_fresh_news()
