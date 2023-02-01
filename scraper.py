import re
from urllib.parse import urlparse
import codecs

searched_list_url = list();

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    list_url = list();
    if (resp.status == 200):
        # print("from: " + resp.raw_response.url)
        cons = codecs.decode(resp.raw_response.content).split(" ")
        for con in cons:
            if(con.startswith("href=\'")):
                url = con.split("\'")[1]
                if (url not in searched_list_url):
                    list_url.append(url)
                    searched_list_url.append(url)
            elif(con.startswith("href=\"")):
                url = con.split("\"")[1]
                if (url not in searched_list_url):
                    list_url.append(url)
                    searched_list_url.append(url)
    return list_url


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        str_hostname = str(parsed.hostname)
        if "ics.uci.edu/" not in str_hostname and "stat.uci.edu" not in str_hostname and "cs.uci.edu/" not in str_hostname and "informatics.uci.edu/" not in str_hostname and "today.uci.edu/department/information_computer_sciences/" not in str_hostname:
            return False
        if parsed.scheme not in set(["http", "https"]):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            +r"|png|tiff?|mid|mp2|mp3|mp4"
            +r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            +r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            +r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            +r"|epub|dll|cnf|tgz|sha1"
            +r"|thmx|mso|arff|rtf|jar|csv"
            +r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
