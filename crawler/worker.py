from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time
import html.parser
import re

class Worker(Thread):

    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)
        
    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = scraper.scraper(tbd_url, resp)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)

        # print
        f = open("rawoutput.txt", "w+")
        list_stopword = list();
        file_stopwords = open("stopword.txt", "r")
        str_stopwords = file_stopwords.readline()
        while len(str_stopwords) > 0:
            str_stopwords = re.sub('[^0-9a-zA-Z]+', '', str_stopwords)
            list_stopword.append(str_stopwords)
            str_stopwords = file_stopwords.readline()
            
        dict_words = scraper.getDictWords()
        sorted_dict_words=dict(sorted(dict_words.items(), key=lambda x:x[1], reverse=True))
        int_count = 0
        print("Longest Site: " + str(scraper.int_max))
        print("Words")
        for key in sorted_dict_words.keys():
            f.write(key + " " + str(sorted_dict_words[key]) + "\r\n")
            if(key in list_stopword):
                continue
            if int_count < 50:
                print(key + " " + str(sorted_dict_words[key]))
                int_count += 1
                continue #remove for get all words to file
            break #remove for get all words to file
        f.close()
        
        searched_url=scraper.getURLList()
        print("URLs")
        for url in searched_url:
            print(url)
        
