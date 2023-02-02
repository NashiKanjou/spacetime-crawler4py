import re
import html.parser
from urllib.parse import urlparse

searched_list_url = list();


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def checkNeed(str_url):
    DateRegex = re.compile(r'\d\d\d\d-\d\d')
    DateRegex1 = re.compile(r'\d\d\d\d/\d\d')
    PageRegex = re.compile(r'(page/)(\d)')
    PageRegex1 = re.compile(r'(pages/)(\d)')
    PageRegex2 = re.compile(r'(p=)(\d)')
    tagRegex = re.compile(r'tags/\d')
    commentRegex = re.compile(r'comment-\d')
    postRegex = re.compile(r'posts/\d')
    bibRegex = re.compile(r'\d.bib')
    dr = DateRegex.search(str_url)
    dr1 = DateRegex1.search(str_url)
    pr = PageRegex.search(str_url)
    pr1 = PageRegex1.search(str_url)
    pr2 = PageRegex2.search(str_url)
    pstr = postRegex.search(str_url)
    cmtr = commentRegex.search(str_url)
    bibr = bibRegex.search(str_url)
    tr = tagRegex.search(str_url)
    if(dr or dr1 or pstr or cmtr or bibr or tr):
        return True
    if(pr):
        if(pr.group(1) == "1"):
            return False
        return True
    if(pr1):
        if(pr1.group(1) == "1"):
            return False
        return True
    if(pr2):
        if(pr2.group(1) == "1"):
            return False
        return True
    return False


global count;
count = 0


def extract_next_links(url, resp):
    global count
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    searched_list_url.append(url)
    list_url = list();
    if (resp.status == 200):
        #if(count == 1):
        #    return list_url
        #count += 1
        cons = str(resp.raw_response.content).split(" ")
        for con in cons:
            s_con = html.unescape(con).lower().replace(",", "").replace("%2f", "/").replace("%2d", "-").replace("%3a", ":")
            if('embed?url=' in s_con):
                s_con = s_con.split('embed?url=')[1]
            if('embed&url=' in s_con):
                s_con = s_con.split('embed&url=')[1]
            if(s_con.startswith("href=\'")): 
                url_raw = s_con.split("\'")
                str_url = url_raw[1]
                if(checkNeed(str_url)):
                    continue
                if (str_url not in searched_list_url):
                    list_url.append(str_url)
                    searched_list_url.append(str_url)
            elif(s_con.startswith("href=\"")):
                url_raw = s_con.split("\"")
                str_url = url_raw[1]
                if(checkNeed(str_url)):
                    continue
                if (str_url not in searched_list_url):
                    list_url.append(str_url)
                    searched_list_url.append(str_url)
    return list_url


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        str_hostname = str(parsed.hostname)
        if "ics.uci.edu" not in str_hostname and "stat.uci.edu" not in str_hostname and "cs.uci.edu" not in str_hostname and "informatics.uci.edu" not in str_hostname and "today.uci.edu/department/information_computer_sciences/" not in str_hostname:
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
