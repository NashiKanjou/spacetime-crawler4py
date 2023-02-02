from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time
import html.parser

dict_words = {}
searched_url = list();


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
        int_max = 0
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            
            # get info
            list_raw = list();
            # resp.raw_response.content.split(b'\n')
            int_count = 0
            if (resp.status == 200):
                b_raw = resp.raw_response.content
                raw = ""
                try:
                    raw = b_raw.decode('utf-8')
                except:
                    # raw = b_raw.decode('latin1')
                    raw = str(b_raw)
               
                # raw = raw.replace("\n", " ").replace("\"", "").replace(".", "").replace(",", "").replace("!", "").replace("?", "").replace(";", "").replace(":", "")
                raw = ""
                try:
                    raw = html.unescape(raw).replace("\n", " ")
                except:
                    raw = ""
                """
                f = open("rawoutput.txt", "w+")
                f.write(raw)
                f.close()
                return
                """
                
                str_word = ""
                str_type = ""
                bool_read = True
                char_last = list();
                html_stack = []
                bool_comment = False
                for c in raw:
                    if(c == '<'):
                        # str_type = ""
                        if(bool_read):
                            if(len(str_word) > 0):
                                list_raw.append(str_word)
                                str_word = ""
                                bool_read = False
                                continue
                    if(c == '>' and not bool_read):
                        if(str_word.endswith("--")):
                            bool_comment = False
                            str_word = ""
                            continue
                        bool_read = True
                        # str_type = str_word
                        if(str_word.startswith("/")):
                            str_word = ""
                            if(html_stack):
                                html_stack.pop()
                            continue
                        if not(bool_comment):
                            html_stack.append(str_word)
                        str_word = ""
                        continue
                    
                    if bool_read and not str_type.startswith("/")  and not (str_type.startswith("a ")and str_type == "a" and "span" in str_type and str_type == "p" and str_type == "br" and str_type == "b" and str_type == "i" and str_type == "q" and str_type.startswith("h") and str_type.startswith("p style")):
                        continue
                        
                    str_type = ""
                    if(html_stack):
                        str_type = html_stack[-1]
                    if bool_read and not ("/" not in str_type and str_type == "li" and str_type == "p" and str_type == "br" and str_type == "b" and str_type == "i" and str_type == "q" and str_type.startswith("h") and str_type.startswith("p style")):
                        continue
                    if(c == '\\'):
                        if(char_last):
                            if (char_last[-1] == '\\'):
                                str_word += c
                                char_last.append("")
                            else:
                                char_last.append(c)
                        else:
                            char_last.append(c)
                            if(len(char_last) > 3):
                                char_last.pop()
                        continue
                    if(c == 'n' and char_last):
                        if (char_last[-1] == '\\' and len(str_word) > 0):
                            list_raw.append(str_word)
                            str_word = ""
                            continue
                    str_word += c
                    if(str_word == "!--" and char_last[0] == '<'):
                        bool_comment = True
                    char_last.append(c)
                    if(len(char_last) > 3):
                        char_last.pop()
            
            for rawline in list_raw:
                list_replaced = rawline.split(" ")
                for word in list_replaced:
                    int_count += 1
                    if not (word in dict_words.keys()):
                        dict_words[word] = 1
                    else:
                        dict_words[word] = dict_words[word] + 1
               
            '''         
            page = etree.HTML(html)
            for str_v in page.xpath(u"XPath語法"):
                list_replaced = str_v.split(" ")
                for word in list_replaced:
                    int_count += 1
                    if not (word in dict_words.keys()):
                        dict_words[word] = 1
                    else:
                        dict_words[word] = dict_words[word] + 1
            '''
                        
            if(int_count > int_max):
                int_max = int_count
            # end of get info
            scraped_urls = scraper.scraper(tbd_url, resp)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            rawurl = tbd_url.replace("https://", "").replace("http://", "")
            str_url = ""
            for c in rawurl:
                if c == "/":
                    break
                str_url += c
            if(str_url in searched_url):
                searched_url.append(str_url)
                
            time.sleep(self.config.time_delay)
            
        # print
        f = open("rawoutput.txt", "w+")
        
        list_stopword = list();
        file_stopwords = open("stopword.txt", "r")
        str_stopwods = file_stopwords.readline()
        while len(str_stopwods) > 0:
            list_stopword.append(str_stopwods)
            str_stopwods = file_stopwords.readline()
        sorted(dict_words.items(), key=lambda x:x[1], reverse=True)
        int_count = 0
        print("Longest Site: " + str(int_max))
        print("Words")
        for key in dict_words.keys():
            f.write(key + "\r\n")
            if(key in list_stopword):
                continue
            if int_count < 50:
                print(key + " " + str(dict_words[key]))
                # break
            int_count += 1
        f.close()
        print("URLs")
        for url in searched_url:
            print(url)
        
