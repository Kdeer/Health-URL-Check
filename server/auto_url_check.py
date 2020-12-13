import requests
import re
from multiprocessing import Process
import time
import json

session = requests.Session()


test_ip = "104.219.248.115"

"These two URL are all not safe"
test_url = "www.barclsbkoln.com"
test_url1 = "http://www.reliancefinancebk.com"


'''
first to determine if the URL is safe from the ipvoid search
conditions are:
    1. ipvoid returns 0/115 blacklist contains the IP address.
    2. Find all sites resides in the 
    3. "ARTIST AGAINST 419" doesn't return the active status record
'''
start = time.time()
def ipvoid_ip_check(target_ip):
    ipvoid_url = "https://www.ipvoid.com/ip-blacklist-check/"
    ipvoid_session = requests.Session()
    data = {"ip": target_ip}
    ipvoid_response = ipvoid_session.post(ipvoid_url, data)
    if ipvoid_response.status_code == 200:
        ipvoid_blacklist_result = re.search("POSSIBLY SAFE \d", ipvoid_response.text, re.IGNORECASE)
        # print(ipvoid_blacklist_result.group())
        ipvoid_blacklist_result = ipvoid_blacklist_result.group().split()[-1]
        # print(ipvoid_blacklist_result)
        if int(ipvoid_blacklist_result) == 0:
            print('IP is not in black list')
        else:
            print('IP is in black list')
    else:
        print('No response from ' + ipvoid_url)
    # end = time.time()
    # print(end - start)

def ipvoid_url_check(target_url):
    ipvoid_url = "https://www.urlvoid.com/"
    ipvoid_session = requests.Session()
    data = {"site": target_url}
    ipvoid_response = ipvoid_session.post(ipvoid_url, data)
    # print(ipvoid_response.text)
    blacklist_result = re.search(".\/35", ipvoid_response.text, re.IGNORECASE)
    if blacklist_result is not None:
        blacklist_result = blacklist_result.group()
        if blacklist_result[0] == '0':
            print('URL is not in black list from 35 sites')
        else:
            print('URL is in ' + blacklist_result + ' blacklists')
    else:
        print('No response from ' + ipvoid_url)
    # end = time.time()
    # print(end - start)


def aa419_check(target_url):
    aa419_url = "https://db.aa419.org/fakebankslist.php"
    aa419_session = requests.Session()
    data = {"psearch": target_url}
    aa419_response = aa419_session.get(aa419_url+"?psearch="+target_url)
    # print(aa419_response.text)
    with open('test.html', 'w') as file:
        file.write(aa419_response.text)
    aa419_blacklist_result = re.search("active", aa419_response.text, re.IGNORECASE)
    if aa419_blacklist_result is not None:
        print(aa419_blacklist_result.group())
    else:
        print('The website is clear from aa419')
    # end = time.time()
    # print(end - start)


api_key = 'Your own google safe browsing v4 API key'

#####
# urls need to be in a list, could be used for multiple urls
# ex: urls = [url1, url2, url3]
#####
def google_url_check(urls):
    url_list = []
    for url in urls:
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

    headers = {'Content-type': 'application/json'}
    r = requests.post('https://safebrowsing.googleapis.com/v4/threatMatches:find?', data=data,
        params={'key': api_key},
        headers=headers
    )

    result = r.json()
    print(r.json())
    end = time.time()
    print(end - start)
    return result


if __name__ == '__main__':
    p1 = Process(target=ipvoid_ip_check, args=(test_ip,))
    p1.start()
    p2 = Process(target=aa419_check, args=(test_url,))
    p2.start()
    p3 = Process(target=ipvoid_url_check, args=(test_url,))
    p3.start()
    p4 = Process(target=google_url_check, args=([test_url],))
    p4.start()

