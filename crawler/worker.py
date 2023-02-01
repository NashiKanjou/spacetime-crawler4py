from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time
import codecs

dict_words = {}
serched_url = list();
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
            
            #get info
            list_raw = list();
            if (resp.status == 200):
                raw = codecs.decode(resp.raw_response.content)
                str_word = ""
                str_type = ""
                bool_read = False
                for c in raw:
                    if(c == '<'):
                        str_type = ""
                        list_raw.append(str_word)
                        str_word = ""
                        bool_read = True
                        continue
                    if(c == '>'):
                        bool_read = False
                        str_type = str_word
                        str_word = ""
                        continue
                    if bool_read and not (str_type == "li" and str_type == "p" and str_type == "br" and str_type == "b" and str_type == "i" and str_type == "q" and str_type.startswith("h") and str_type.startswith("p style")):
                        continue
                    str_word += c
            for raw in list_raw:
                list_replaced = raw.replace("\n", " ").split(" ")
                for word in list_replaced:
                    print(word)
                    if not (word in dict_words.keys()):
                        dict_words[word] = 1
                    else:
                        dict_words[word] = dict_words[word] + 1
            
            
            #end of get info
            scraped_urls = scraper.scraper(tbd_url, resp)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            serched_url.append(tbd_url)
            time.sleep(self.config.time_delay)
        #print
        print("Words")
        for key in dict_words.keys():
            print(key+" "+dict_words[key])
        print("URLs")
        for url in serched_url:
            print(url)