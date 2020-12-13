
import requests
import re
from urllib.parse import urljoin

'''
Usage: 
    level = 2
    url = "http://10.0.2.6/mutillidae"
    ignore_links = ["http://10.0.2.6/mutillidae/index.php?page=login.php"]
    c = Crawler(level, url, ignore_links)
    c.crawl()
    c.get_link_list()

Note: when test on Internet website, level = 3's waiting time is very long. Better ask for the website owner's permission before use any level > 2.
'''




class Crawler:
    def __init__(self, level, url, ignore_links=None):
        self.session = requests.Session()
        self.links_to_ignore = ignore_links
        self.level = level
        self.target_url = url
        self.link_list = []
        self.level_dict = {}

    def request(self):
        try:
            return requests.get(self.url)
        except requests.exceptions.ConnectError:
            pass

    def extract_url(self, url):
        resposne = self.session.get(url)
        links = re.findall('(?:href=")(.*?)"', resposne.content.decode(errors="ignore"))
        return links

    def crawl(self):
        self.crawl_aux(self.level, self.target_url)

    def crawl_aux(self, level, url=None):
        if level > 0:
            if url is None:
                url = self.target_url

            href_links = self.extract_url(url)

            for link in href_links:
                link = urljoin(url, link)
                if '#' in link:
                    link = link.split("#")[0]

                if link not in self.link_list and link not in self.links_to_ignore:
                    self.link_list.append(link)
                    self.crawl_aux(level-1, link)

    def get_link_list(self):
        print(self.link_list)
        print("list length:", len(self.link_list))
        return self.link_list




















