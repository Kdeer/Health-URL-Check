import json
import requests
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import certifi
import whois
import datetime


def check_is_same_origin(url1, url2):
    obj1, obj2 = urlparse(url1), urlparse(url2)
    return obj1.hostname == obj2.hostname


class FeatureGetter:
    def __init__(self, url):
        self.url = url
        self.urlObj = urlparse(self.url)
        self.domain_reg = domain_reg_len(self.url)
        try:
            self.response = requests.get(url)
            self.redirect_times = len(self.response.history)
            self.dom = BeautifulSoup(self.response.text)
        except Exception as e:
            self.dom = None
            print(e)

    def run(self):
        requests.get(self.url)

    def call_function(self, function_name):
        if function_name == "function8":
            return self.function8()
        elif function_name == "function9":
            return self.function9()
        elif function_name == "function10":
            return self.function10()
        elif function_name == "function13":
            return self.function13()
        elif function_name == "function14":
            return self.function14()
        elif function_name == "function15":
            return self.function15()
        elif function_name == "function16":
            return self.function16()
        elif function_name == "function17":
            return self.function17()
        elif function_name == "function18":
            return self.function18()
        elif function_name == "function19":
            return self.function19()
        elif function_name == "function20":
            return self.function20()
        elif function_name == "function21":
            return self.function21()
        elif function_name == "function22":
            return self.function22()
        elif function_name == "function23":
            return self.function23()
        elif function_name == "function24":
            return self.function24()
        elif function_name == "function25":
            return self.function25()
        elif function_name == "function26":
            return self.function26()
        elif function_name == "function27":
            return self.function27()
        elif function_name == "function28":
            return self.function28()
        elif function_name == "function29":
            return self.function29()
        elif function_name == "function30":
            return self.function30()
        else:
            return 1

    def function8(self):
        """
        1.1.8 HTTPS
        Use https and Issuer is trusted and age of certificate >= 1 years => legitimate 1
            for now, we take off the >= 1 years condition
        using https and issuer is not trusted => suspicious => 0
        otherwise => phising => -1
        """
        s = requests.Session()
        if "http" not in self.url:
            link = "https://" + self.url
        else:
            link_arr = self.url.split("://")
            link = link_arr[0] + "s://" + link_arr[1]
        try:
            resposne = s.get(link, verify=certifi.where(), timeout=3)
            if resposne.status_code:
                return 1
        except requests.exceptions.SSLError:
            print("The ssl is not trusted")
            return 0
        except requests.exceptions.ConnectionError:
            print("The site has no SSL")
            return -1

    def function9(self):
        """
        1.1.9 Domain Registration Length
        Domain Expires in less than a year => phising => -1
        otherwise => legitimate => 1
        requires python-whois API: https://pypi.org/project/python-whois/
        :return:
        """
        return self.domain_reg[2]

    def function10(self):
        """
        1.1.10.	Favicon

        - 从外部域加载Favicon -> -1
        - 否则 -> 1
        :return:
        """
        if not self.dom:
            return 1
        links = self.dom.head.find_all('link')
        for link_element in links:
            if link_element.attrs['href'].find('icon') >= 0 and \
                    not check_is_same_origin(link_element.attrs['href'], self.url):
                return -1
        return 1

    def function13(self):
        """
        1.2.1. Request URL

        外部对象（img, video, audio）中外链的占比
        - [0, 22%) -> 1
        - [22%, 61%) -> 0
        - [61%, 100%] -> -1
        :return:
        """
        if not self.dom:
            return 1
        total_num, out_link_num = 0, 0
        imgs = self.dom.find_all('img')
        total_num += len(imgs)
        videos = self.dom.find_all('video')
        total_num += len(videos)
        audios = self.dom.find_all('audio')
        total_num += len(audios)

        for img in imgs:
            if not check_is_same_origin(img.attrs['src'], self.url):
                out_link_num += 1
        for video in videos:
            if not check_is_same_origin(video.attrs['src'], self.url):
                out_link_num += 1
        for audio in audios:
            if not check_is_same_origin(audio['src'], self.url):
                out_link_num += 1

        rate = float(out_link_num) / total_num
        if rate < 0.22:
            return 1
        elif rate < 0.61:
            return 0
        else:
            return -1

    def function14(self):
        """
        1.2.2. URL of Anchor

        所有a标签中，空标签的占比
        - [0, 31%) => 1
        - [31%, 67%) => 0
        - [67%, 100%] => -1
        :return:
        """
        if not self.dom:
            return 1
        a_elements, anchor_num = self.dom.find_all('a'), 0
        for a in a_elements:
            if a.attrs['href'] == 'javascript:void(0)':
                anchor_num += 1
        rate = float(anchor_num) / len(a_elements)
        if rate < 0.31:
            return 1
        elif rate < 0.67:
            return 0
        else:
            return -1

    def function15(self):
        """
        1.2.3. Links in <Meta>, <Script> and <Link> tags

        <script>、<link>中包含的外链的比例
        - [0, 17%) => 1
        - [17%, 81%) => 0
        - [81%, 100%] => -1
        :return:
        """
        if not self.dom:
            return 1
        script_elements = self.dom.find_all('script')
        link_elements = self.dom.find_all('link')
        total_num, out_num = len(script_elements) + len(link_elements), 0
        for script in script_elements:
            if not check_is_same_origin(script.attrs['src'], self.url):
                out_num += 1
        for link_element in link_elements:
            if not check_is_same_origin(link_element.attrs['href'], self.url):
                out_num += 1
        rate = float(out_num) / total_num
        if rate < 0.17:
            return 1
        elif rate < 0.81:
            return 0
        else:
            return -1

    def function16(self):
        """
        1.2.4. Server Form Handler (SFH)

        - SHF is "about:blank" or "" => -1
        - SFH is not same origin => 0
        - else => -1
        :return:
        """
        if not self.dom:
            return 1
        forms = self.dom.find_all('form')
        for form in forms:
            if "about:blank".find(form.attrs['action']) >= 0:
                return -1
            elif check_is_same_origin(self.url, form.attrs['action']):
                return 0
        return 1

    def function17(self):
        """
        1.2.5 mailTo or mail() function in the html page
        if mail() or mailto: function exists => phishing => -1
        if not => legitimate => 1
        :return:
        """
        return mail_func(self.url)

    def function18(self):
        """
        1.2.6 Abnormal URL, this one will be done in 1.1.9
        if the host name is not included in the URL => phising => -1
        if the host name is included in the URL => legitimate => 1
        :return:
        """
        return self.domain_reg[1]

    def function19(self):
        """
        1.3.1 Website Forwarding
        If the redirect page number is <= 1 -> legitmate => 1
        If the redirect page is >= 2 and < 4 -> suspicious => 0
        otherwise -> phishing => -1
        """
        if not self.redirect_times:
            return 1
        if self.redirect_times <= 1:
            return 1
        elif self.redirect_times < 4:
            return 0
        else:
            return -1

    def function20(self):
        """
        1.3.2. Status Bar Customization

        - Use history.putState to change display of url => -1
        - else => 1
        :return:
        """
        if not self.dom:
            return 1
        scripts = self.dom.find_all('script')
        for script in scripts:
            if script.text.find('history.putState') >= 0:
                return -1
        return 1

    def function21(self):
        """
        1.3.3. Disabling Right Click

        - 禁用右键单击 => -1
        - else => 1
        :return:
        """
        if not self.dom:
            return 1
        scripts = self.dom.find_all('script')
        for script in scripts:
            if script.text.find('event.button == 2') >= 0 and \
                    script.text.find('false'):
                return -1
        return 1

    def function22(self):
        """
        1.3.4. Using Pop-up Window

        - scripts content window.open or window.prompt  => -1
        - else => 1
        :return:
        """
        if not self.dom:
            return 1
        scripts = self.dom.find_all('script')
        for script in scripts:
            if script.text.find('window.open') >= 0 or \
                    script.text.find('window.prompt'):
                return -1
        return 1
        pass

    def function23(self):
        """
        1.3.5. IFrame Redirection

        - Use iframe => -1
        - else => 1
        :return:
        """
        if not self.dom:
            return 1
        if len(self.dom.find_all('iframe')) > 0:
            return -1
        return 1

    def function24(self):
        """
        1.4.1 Age of Domain
        Age of Domain >= 6 month => legitimate => 1
        otherwise => phishing => -1
        :return:
        """
        return self.domain_reg[0]

    def function25(self):
        """
        1.4.2 DNS Record
        if not found in DNS record -> phising => -1
        otherwise -> legitimate => 1
        :return:
        """
        return self.domain_reg[3]

    def function26(self):
        """
        1.4.3 Website Traffic, use the rank from Alexa.com
        if website Rank < 100,000 -> legitimate => 1
        if website rank > 100,000 -> suspicious => 0
        otherwise -> phish => -1
        :return:
        """
        return website_rank(self.url)

    def function27(self):
        """
        1.4.4 PageRank
        if pageRank < 0.2 -> phising => -1
        otherwise legitimate => 1
        Difficult to find the source to determine the page rank, will hold for now
        :return:
        """
        pass

    def function28(self):
        """
        1.4.5 Google Index, test whether the url is in google's index
        if in the google index -> legitimate => 1
        otherwise -> phishing => -1

        library used: pip install google
        usage: https://www.geeksforgeeks.org/performing-google-search-using-python-code/
        :return:
        """
        return google_index(self.url)

    def function29(self):
        """
        1.4.6 Number of Links Pointing to Page
        if link pointing to the webpage = 0 -> phising => -1
        if link pointing to the webpage > 0 and <=2 -> suspicious = 0
        otherwise -> legitimate => 1

        problem: google's link operator is deprecated
        https://www.openlinkprofiler.org/  is used as an alternative solution
        :return:
        """
        return pointing_links(self.url)

    def function30(self):
        """
        1.4.7 Statistical reports based feature
        Something need to be changed

        if host is found in google safe browse api or aa419 -> phising => -1
        otherwise -> legitmate => 1
        :return:
        """
        return statistical_report(self.url)


'''
1.4.7 Statistical reports based feature
Something need to be changed

if host is found in google safe browse api or aa419 -> phising => -1
otherwise -> legitmate => 1
'''


def statistical_report(url):
    url_list = []
    url_list.append({"url": url})
    print(url_list)
    data = json.dumps({
        "client": {
            "clientId": "xxxx",
            "clientVersion": "1.5.2"
        },
        "threatInfo": {
            "threatTypes": ["THREAT_TYPE_UNSPECIFIED", "MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE",
                            "POTENTIALLY_HARMFUL_APPLICATION"],
            "platformTypes": ["ALL_PLATFORMS"],
            "threatEntryTypes": ["URL"],
            "threatEntries": url_list
        }
    })
    api_key = "enter the api"
    headers = {'Content-type': 'application/json'}
    r = requests.post('https://safebrowsing.googleapis.com/v4/threatMatches:find?', data=data,
                      params={'key': "enter the api"},
                      headers=headers
                      )

    result = r.json()
    print(len(result), result)

    if len(result) > 0:
        return -1

    aa419_url = "https://db.aa419.org/fakebankslist.php"
    aa419_session = requests.Session()
    data = {"psearch": url}
    aa419_response = aa419_session.get(aa419_url + "?psearch=" + url)
    # print(aa419_response.text)
    aa419_blacklist_result = re.search("active&nbsp", aa419_response.text, re.IGNORECASE)
    if aa419_blacklist_result is not None:
        print("it is not none")
        return -1
    else:
        print('The website is clear from aa419')
        return 1


# statistical_report("www.barclsbkoln.com")
# statistical_report("www.wego-club.com")


'''
1.4.6 Number of Links Pointing to Page
if link pointing to the webpage = 0 -> phising => -1
if link pointing to the webpage > 0 and <=2 -> suspicious = 0
otherwise -> legitimate => 1

problem: google's link operator is deprecated
https://www.openlinkprofiler.org/  is used as an alternative solution
'''


def pointing_links(link):
    if "https://" in link:
        link = link[8:]
    if "http://" in link:
        link = link[7:]
    if "www." in link:
        link = link[4:]
    s = requests.Session()

    open_link_url = "https://www.openlinkprofiler.org/r/" + link
    response = s.get(open_link_url)
    link_result = re.search('Sorry, we do not store', response.content.decode(errors="ignore"))
    print(link_result)
    print(response.text)


'''
1.4.5 Google Index, test whether the url is in google's index
if in the google index -> legitimate => 1
otherwise -> phishing => -1

library used: pip install google
usage: https://www.geeksforgeeks.org/performing-google-search-using-python-code/
'''

from googlesearch import search


def google_index(link):
    result = -1

    query = "site:" + link
    index_list = search(query, tld="co.in", num=1, stop=1, pause=2)

    for x in index_list:
        result += 1
        if result > -1:
            result = 1
            print(result)
            return result

    print(result)
    return result


# google_index("fakeurl.com")


'''
1.4.4 PageRank
if pageRank < 0.2 -> phising => -1
otherwise legitimate => 1
Difficult to find the source to determine the page rank, will hold for now
'''

'''
1.4.3 Website Traffic, use the rank from Alexa.com 
if website Rank < 100,000 -> legitimate => 1
if website rank > 100,000 -> suspicious => 0
otherwise -> phish => -1
'''


def website_rank(link):
    result = -1
    if "https://" in link:
        link = link[8:]
    if "http://" in link:
        link = link[7:]
    if "www." in link:
        link = link[4:]
    alexa_database_url = "https://www.alexa.com/siteinfo/" + link

    s = requests.Session()
    response = s.get(alexa_database_url)

    web_rank_result = re.search('(?:<span class="hash">#<\/span>)(.*)', response.content.decode(errors="ignore"))

    if web_rank_result:
        rank_list = web_rank_result.group(1).strip().split(',')

        if len(rank_list) == 1:
            result = 1
        elif len(rank_list) == 2:
            if int(rank_list[0]) <= 100:
                result = 1
            else:
                result = 0
        else:
            result = 0
        print(rank_list)

    print(result)
    return result


# link = "wego-club.com"
# website_rank(link)


'''
1.2.5 mailTo or mail() function in the html page
if mail() or mailto: function exists => phishing => -1
if not => legitimate => 1
'''


def mail_func(link):
    s = requests.Session()
    response = s.get(link)
    if response.status_code == 200:
        mail_result = re.search('mailto:.*?@.*?>', response.content.decode(errors="ignore"))
        if mail_result:
            print(mail_result.group())
            return -1
    return 1


# mail_func("https://www.w3schools.com/tags/tryit.asp?filename=tryhtml_link_mailto")


'''
1.1.9 Domain Registration Length
Domain Expires in less than a year => phising => -1
otherwise => legitimate => 1
requires python-whois API: https://pypi.org/project/python-whois/

1.2.6 Abnormal URL, this one will be done in 1.1.9
if the host name is not included in the URL => phising => -1
if the host name is included in the URL => legitimate => 1

1.4.1 Age of Domain
Age of Domain >= 6 month => legitimate => 1
otherwise => phishing => -1

1.4.2 DNS Record
if not found in DNS record -> phising => -1
otherwise -> legitimate => 1

timeout could be a trouble
whois creation date will reset if a domain is expired and then claimed by someone else
https://www.expireddomains.net/faq/#:~:text=If%20you%20register%20a%20Deleted,and%20a%20new%20Creation%20Date.&text=The%20domain%20will%20still%20be%20deleted%20and%20the%20Whois%20Record%20resets.
'''


def domain_reg_len(link):
    try:
        response = whois.whois(link)
        # 1.4.2
        dns_record = 1

        # 1.2.6
        domain_url = 0
        if response.domain_name:
            if type(response.domain_name) == list:
                domain_name = response.domain_name[0].lower()
            else:
                domain_name = response.domain_name.lower()
            domain_in_url = re.search(domain_name, link.lower())
            if domain_in_url:
                domain_url = 1
            else:
                domain_url = -1

        # 1.4.1
        domain_days = 0

        if response.creation_date and response.expiration_date:
            if type(response.creation_date) == list:
                days = response.expiration_date[0] - response.creation_date[0]
            else:
                days = response.expiration_date - response.creation_date
            days = days.days
            print(days)
            if days > 365:
                domain_days = 1
            else:
                domain_days = -1

            # 1.1.9
            domain_expire_days = 0
            date_now = datetime.datetime.now()
            if type(response.expiration_date) == list:
                expiration = response.expiration_date[0] - date_now
            else:
                expiration = response.expiration_date - date_now
            if expiration.days > 365:
                domain_expire_days = 1
            else:
                domain_expire_days = -1

        print(domain_days, domain_url, domain_expire_days, dns_record)
        return domain_days, domain_url, domain_expire_days, dns_record
    except whois.parser.PywhoisError:
        domain_days = -1
        domain_url = -1
        domain_expire_days = -1
        dns_record = -1
        return domain_days, domain_url, domain_expire_days, dns_record

# domain_reg_len('google.com')

# domain_reg_len('renren.com')
# domain_reg_len('www.stackoverflow.com')


# link = "https://www.aba.myspecies.info"
# verify_ssl(link)
