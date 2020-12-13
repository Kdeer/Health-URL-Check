import json
import requests
import re
import csv
import time
import random

'''
1.3.1 Website Forwarding
If the redirect page number is <= 1 -> legitmate => 1
If the redirect page is >= 2 and < 4 -> suspicious => 0
otherwise -> phishing => -1
'''

# not tested yet
def web_forward(url):
    s = requests.Session()

    response = s.get(url)
    print(response.history)


link = "www.wego-club.com"
web_forward(link)




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
            "threatTypes": ["THREAT_TYPE_UNSPECIFIED", "MALWARE", "SOCIAL_ENGINEERING","UNWANTED_SOFTWARE","POTENTIALLY_HARMFUL_APPLICATION"],
            "platformTypes": ["ALL_PLATFORMS"],
            "threatEntryTypes": ["URL"],
            "threatEntries": url_list
        }
    })
    api_key = "enter the api"
    headers = {'Content-type': 'application/json'}
    r = requests.post('https://safebrowsing.googleapis.com/v4/threatMatches:find?', data=data,
        params={'key': "AIzaSyC9bYu6ok7-sEpjZdd7kxG4ggZgE8CgkBo"},
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

    query = "site:"+link
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
import whois
import datetime
def domain_reg_len(link):

    try:

        response = whois.whois(link)
        # 1.4.2
        dns_record = 1

        # 1.2.6
        domain_url = 0
        if response.domain_name:
            domain_name = response.domain_name.lower()
            if type(domain_name) == list:
                domain_name = domain_name[0].lower()
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
        print("the link provided is not valid")


# domain_reg_len('google.com')

# domain_reg_len('renren.com')
# domain_reg_len('www.stackoverflow.com')



'''
1.1.8 HTTPS 
Use https and Issuer is trusted and age of certificate >= 1 years => legitimate 1
    for now, we take off the >= 1 years condition
using https and issuer is not trusted => suspicious => 0
otherwise => phising => -1
'''

import socket
import certifi

def verify_cert(link):
    s = requests.Session()
    if "http" not in link:
        link = "https://" + link
    else:
        link_arr = link.split("://")
        link = link_arr[0] + "s://" + link_arr[1]
    print(link)

    try:
        resposne = s.get(link,  verify=certifi.where(), timeout=3)
        if resposne.status_code:
            return 1
    except requests.exceptions.SSLError:
        print("The ssl is not trusted")
        return 0
    except requests.exceptions.ConnectionError:
        print("The site has no SSL")
        return -1

# link = "https://www.aba.myspecies.info"
# verify_ssl(link)