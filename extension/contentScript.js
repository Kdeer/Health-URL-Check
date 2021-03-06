/**
 * Try to get some item in localstorage, which these item's key in keys
 * @param keys
 * @returns {Promise<{[key: string]:any}>}
 */
function getLocalStorageAsync(keys) {
    return new Promise((resolve, reject) => {
        chrome.storage.local.get(keys, result => {
            for (let i = 0; i < keys.length; i++) {
                if (!!result[keys[i]])
                    resolve(result);
            }
            reject(new Error("Not found"));
        });
    })
}

/**
 *
 * @param host
 * @returns {Promise<boolean>}
 */
function canTrust(host) {
    let currentHost = host;
    return getLocalStorageAsync([currentHost])
        .then(res => {
            return Promise.resolve(true);
        })
        .catch(err => {
            // complete host can not be trust
            const names = currentHost.split(".");
            const hosts = [];
            for (let i = 0; i < names.length - 1; i++) {
                currentHost = currentHost.substr(names[i].length + 1, currentHost.length - names[i].length - 1);
                hosts.push(currentHost);
            }
            return getLocalStorageAsync(hosts);
        })
        .then(res => {
            const keys = Object.keys(res);
            for (let i = 0; i < keys.length; i++) {
                if (!!res[keys[i]]) {
                    return Promise.resolve(true);
                }
            }
            return Promise.resolve(false);
        })
}

async function asyncFilter(arr, predicate) {
    const results = await Promise.all(arr.map(predicate));
    return arr.filter((_v, index) => results[index]);
}

/**
 *
 * @param element
 * @param securityLevel     0 => security
 *                          1 => warning
 *                          2 => dangerous
 */
function changeAElementToTipUser(element, securityLevel) {
    switch (securityLevel) {
        case 0:
            break
        case 1:
            element.title = "Warning: this url may be dangerous";
            element.style = "border: solid #FFA500 1px";
            break;
        case 2:
        default:
            element.title = "Dangerous: this url is dangerous";
            element.style = "border: solid red 2px";
            break;

    }
}


(async () => {
    // Get all a element in this page
    const aElements = document.getElementsByTagName("a");
    const requestData = {};
    let links = [];
    for (let i = 0; i < aElements.length; i++) {
        const item = aElements.item(i);
        if (!!item.host) {
            if (!requestData[item.host]) {
                requestData[item.host] = [];
            }
            requestData[item.host].push({
                element: item,
                url: item.href
            });
        }
    }
    for (let key in requestData) {
        links.push({
            host: key,
            urls: requestData[key]
        });
    }

    // filter not trust host and it's urls
    links = await asyncFilter(links, async item => {
        try {
            return !await canTrust(item.host)
        } catch (err) {

        }
        return true;
    });
    const tmpObj = [];
    links.forEach(item => {
        item.urls.forEach(item => {
            tmpObj.push({
                ...item
            });
        })
    })
    const promises = [];
    tmpObj.forEach(item => {
        item.element.addEventListener('mouseover', () => {
            // mouse hover the a element
            if (!item.isHover) {
                item.isHover = true;
                // do after hover
                if (item.isSecurity !== undefined) {
                    changeAElementToTipUser(item.element, item.isSecurity ? 0 : 2);
                } else {
                    item.isSecurity = true;
                    changeAElementToTipUser(item.element, item.isSecurity ? 0 : 2);

                    // First get feature local
                    new FeatureGetter(item.url, location.href)
                        .run()
                        .then(res => {
                            item.features = res;
                            return Promise.resolve();
                        })
                        .catch(err => {
                            item.features = {};
                            return Promise.resolve();
                        })
                        .then(() => {
                            // request server to judge whether this url is safe
                            return fetch("http://localhost:5000/checkUrl", {
                                method: 'POST',
                                mode: 'cors',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({
                                    url: item.url,
                                    features: item.features
                                })
                            })
                        })
                        .then(res => {
                            return res.json()
                        })
                        .then(res => {
                            item.isSecurity = res.data.security;
                            changeAElementToTipUser(item.element, item.isSecurity ? 0 : 2);
                        })
                        .catch(err => {
                            console.log("====> ", err);
                        })
                }
            }
        });
        item.element.addEventListener('mouseout', () => {
            // mouse leave the a element
            if (!!item.isHover) {
                item.isHover = false;
            }
        });
    });
})();

////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//// Get Features
////////////////////////////////////////////////////////////////////////////////////////////////////////////////


class FeatureGetter {

    constructor(url, originUrl) {
        this.url = url;
        this.originUrl = originUrl
    }

    checkIsSameOrigin(url1, url2) {
        const urlObj1 = new URL(url1);
        const urlObj2 = new URL(url2);
        return urlObj1.hostname === urlObj2.hostname;
    }

    /**
     * 1.1.1.    Using the IP Address
     *If an IP address is used as an alternative of the domain name in the URL, such as “http://125.98.3.123/fake.html”,
     * it could be regarded as a phishing link
     * If The Domain Part has an IP Address     => Phishing->-1
     * Otherwise    => Legitimate->1
     */
    function1(url) {
        const urlObj = new URL(url);
        const slices = urlObj.host.split(".");
        if (slices.length !== 4)
            return 1;
        for (let i = 0; i < slices.length; i++) {
            if (isNaN(parseInt(slices[i])))
                return 1;
        }
        return -1;
    }

    /**
     * 1.1.2.    Long URL to Hide the Suspicious Part
     *If the length of the URL is greater than or equal to 54 characters, the URL is classified as phishing
     * URL's length <= 54   => Legitimate -> 1
     * 54 < URL's length <= 75   => Suspicious -> 0
     * otherwise   => Phishing->-1
     */
    function2(url) {
        if (url.length <= 54)
            return 1;
        else if (url <= 75)
            return 0;
        else
            return -1;
    }

    /**
     * 1.1.3.    Using URL Shortening Services “TinyURL”
     *
     * Short URL (http redirect) => Phishing -> -1
     * otherwise => Legitimate -> 1
     * @param response
     */
    function3(response) {
        if (response.redirected) {
            return -1;
        }
        return 1;
    }

    /**
     * 1.1.4.    URL’s having “@” Symbol
     *
     * url has @ symbol      => Phishing -> -1
     * therwise     => Legitimate -> 1
     * @param url
     * @returns {number}
     */
    function4(url) {
        if (url.indexOf("@") >= 0) {
            return -1;
        }
        return 1;
    }

    /**
     * 1.1.5.    Redirecting using “//”
     *
     * ThePosition of the Last Occurrence of "//\" " in the URL > 7     => Phishing -> -1
     * therwise     => Legitimate -> 1
     * @param url
     * @returns {number}
     */
    function5(url) {
        if (url.lastIndexOf("//") > 7) {
            return -1;
        }
        return 1;
    }

    /**
     * 1.1.6.    Adding Prefix or Suffix Separated by (-) to the Domain
     *
     * Domain Name Part Includes (-) Symbol => Phishing -> -1
     * otherwise     => Legitimate ->1
     * @param url
     * @returns {number}
     */
    function6(url) {
        const urlObj = new URL(url);
        if (urlObj.hostname.indexOf("-") >= 0) {
            return -1;
        }
        return 1;
    }

    /**
     * 1.1.7.    Sub Domain and Multi Sub Domains
     *
     * After ignoring www and ccTLD in the url, the rest part:
     * Dots In Domain Part = 1    => Legitimate -> 1
     * Dots In Domain Part = 2    => Suspicious -> 0
     * Otherwise    => Phishing -> -1
     * @param url
     */
    function7(url) {
        let hostname = new URL(url).hostname;
        if (hostname.startsWith("www.")) {
            hostname = hostname.substring(4);
        }
        hostname = hostname.substring(0, hostname.lastIndexOf("."));
        const itemNum = hostname.split(".");
        if (itemNum <= 2) {
            return 1;
        } else if (itemNum <= 3) {
            return 0;
        } else {
            return -1;
        }
    }

    /**
     * 1.1.10.    Favicon
     *
     *  If the favicon is loaded from a domain other than that shown in the address bar => Phishing -> -1
     *  Otherwise     => Legitimate ->1
     * @param dom
     * @param url
     * @returns {number}
     */
    function10(dom, url) {
        if (dom == null) {
            return 1;
        }
        const links = document.head.getElementsByTagName("link")
        const urlObj = new URL(url);
        for (let i = 0; i < links.length; i++) {
            if (links.item(i).rel.indexOf("icon") >= 0 && new URL(links.item(i).href).host !== urlObj.host) {
                return -1;
            }
        }
        return 1;
    }

    /**
     * 1.1.11.    Using Non-Standard Port
     *
     * [21, 22, 23, 80, 443, 445, 1433, 1521, 3306, 3389]
     * port is the preferred port    => Phishing -> -1
     *  otherwise     => Legitimate ->1
     * @param url
     */
    function11(url) {
        const urlObj = new URL(url);
        if ("21-22-23-80-443-445-1433-1521-3306-3389".indexOf(urlObj.port) >= 0) {
            return 1;
        }
        return -1;
    }

    /**
     * 1.1.12.    The Existence of “HTTPS” Token in the Domain Part of the URL
     *
     * Using HTTP Token in Domain Part of The URL   => Phishing -> -1
     *  otherwise     => Legitimate ->1
     * @param url
     * @returns {number}
     */
    function12(url) {
        const urlObj = new URL(url);
        if (urlObj.hostname.indexOf("http")) {
            return -1;
        }
        return 1;
    }

    /**
     * 1.2.1. Request URL
     *
     * the % of external objects contained within a webpage such as images, videos and sounds are loaded from
     * another domain
     * % of Request URL <22%   => Legitimate -> 1
     * % of Request URL≥22% and 61%    => Suspicious -> 0
     * Otherwise    => Phishing -> -1
     * @param dom
     * @param url
     * @returns {number}
     */
    function13(dom, url) {
        if (dom == null)
            return 1;
        let totalNum = 0;
        let outLinksNum = 0;
        const imgs = dom.getElementsByTagName("img");
        totalNum += imgs.length;
        const videos = dom.getElementsByTagName("video");
        totalNum += videos.length;
        const audios = dom.getElementsByTagName("audio");
        totalNum += audios.length;

        for (let i = 0; i < imgs.length; i++) {
            try {
                if (!this.checkIsSameOrigin(imgs.item(i).src, url)) {
                    outLinksNum++;
                }
            } catch (err) {

            }
        }

        for (let i = 0; i < videos.length; i++) {
            try {
                if (!this.checkIsSameOrigin(videos.item(i).src, url)) {
                    outLinksNum++;
                }
            } catch (err) {

            }
        }

        for (let i = 0; i < audios.length; i++) {
            try {
                if (!this.checkIsSameOrigin(audios.item(i).src, url)) {
                    outLinksNum++;
                }
            } catch (err) {

            }
        }

        const rate = outLinksNum / totalNum;
        if (rate < 0.22)
            return 1;
        else if (rate < 0.61)
            return 0;
        else
            return -1;
    }

    /**
     * 1.2.2. URL of Anchor
     *If the <a> tags and the website have different domain names or does not link to any webpage
     * % of URL Of Anchor [0, 31%) => Legitimate -> 1
     * % of URL Of Anchor [31%, 67%) => Suspicious -> 0
     * Otherwise => Phishing -> -1
     * @param dom
     * @returns {number}
     */
    function14(dom) {
        if (dom == null)
            return 1;
        const aElements = dom.getElementsByTagName("a");
        let anchorNum = 0;
        for (let i = 0; i < aElements.length; i++) {
            if (aElements.item(i).href === "javascript:void(0)") {
                anchorNum++;
            }
        }
        const rate = anchorNum / aElements.length;
        if (rate < 0.31)
            return 1;
        else if (rate < 0.67)
            return 0;
        else
            return -1;
    }

    /**
     * 1.2.3. Links in <Meta>, <Script> and <Link> tags
     *
     * Ratio of external links included in < SCRIPT > , < Link >
     * % of Links in "<Meta>","<Script>" and "<"Link> is [0, 17%) => Legitimate -> 1
     * % of Links in <Meta>","<Script>" and "<"Link> is [17%, 81%) => Suspicious -> 0
     * Otherwise => Phishing -> -1
     * @param dom
     * @param url
     * @returns {number}
     */
    function15(dom, url) {
        if (dom == null)
            return 1;
        try {
            const scriptElements = dom.getElementsByTagName("script");
            const linkElements = dom.getElementsByTagName("link");
            const totalNum = scriptElements.length + linkElements.length;
            let outLinkNum = 0;
            for (let i = 0; i < scriptElements.length; i++) {
                if (!this.checkIsSameOrigin(scriptElements.item(i).src, url))
                    outLinkNum++;
            }
            for (let i = 0; i < linkElements.length; i++) {
                if (!this.checkIsSameOrigin(linkElements.item(i).href, url))
                    outLinkNum++;
            }
            const rate = outLinkNum / totalNum;
            if (rate < 0.17) {
                return 1;
            } else if (rate < 0.81) {
                return 0;
            } else {
                return -1;
            }
        } catch (err) {
            return 1;
        }
    }

    /**
     * 1.2.4. Server Form Handler (SFH)
     *
     * SHF is "about:blank" or "" => Phishing -> -1
     * SFH is not same origin => Suspicious -> 0
     * Otherwise => Legitimate -> 1
     * @param dom
     * @param url
     * @returns {number}
     */
    function16(dom, url) {
        if (dom == null)
            return 1;
        const forms = dom.getElementsByTagName("form");
        for (let i = 0; i < forms.length; i++) {
            if ("about:blank".indexOf(forms.item(i).action) >= 0) {
                return -1;
            } else if (!this.checkIsSameOrigin(forms.item(i).action, url)) {
                return 0;
            }
        }
        return 1;
    }

    /**
     * 1.3.2. Status Bar Customization
     *
     * Use history.putState to change display of url => Phishing -> -1
     * Otherwise => Legitimate -> 1
     * @param dom
     * @returns {number}
     */
    function20(dom) {
        if (dom == null)
            return 1;
        const scripts = dom.getElementsByTagName("script");
        for (let i = 0; i < scripts.length; i++) {
            if (scripts.item(i).innerHTML.indexOf("history.putState") >= 0)
                return -1;
        }
        return 1;
    }

    /**
     * 1.3.3. Disabling Right Click
     *
     * Right Click Disabled => Phishing -> -1
     * Otherwise => Legitimate -> 1
     * @param dom
     * @returns {number}
     */
    function21(dom) {
        if (dom == null)
            return 1;
        const scripts = dom.getElementsByTagName("script");
        for (let i = 0; i < scripts.length; i++) {
            if (scripts.item(i).innerHTML.indexOf("event.button == 2") >= 0 &&
                scripts.item(i).innerHTML.indexOf("false"))
                return -1;
        }
        return 1;
    }

    /**
     * 1.3.4. Using Pop-up Window
     *
     * scripts content window.open or window.prompt  => Phishing -> -1
     * Otherwise => Legitimate -> 1
     * @param dom
     */
    function22(dom) {
        if (dom == null)
            return 1;
        const scripts = dom.getElementsByTagName("script");
        for (let i = 0; i < scripts.length; i++) {
            if (scripts.item(i).innerHTML.indexOf("window.open") >= 0 ||
                scripts.item(i).innerHTML.indexOf("window.prompt") >= 0) {
                return -1;
            }
        }
        return 1;
    }

    /**
     * 1.3.5. IFrame Redirection
     *
     * Use iframe => Phishing -> -1
     * Otherwise => Legitimate -> 1
     * @param dom
     * @returns {number}
     */
    function23(dom) {
        if (dom == null)
            return 1;
        if (dom.getElementsByTagName("iframe").length > 0) {
            return -1;
        }
        return 1;
    }

    run() {
        //When an HTTPS site contains an HTTP link, or when the URL is an external link, only 7 features are counted in front-end
        if ((this.originUrl.startsWith('https://') && this.url.startsWith("http://")) || !this.checkIsSameOrigin(this.url, this.originUrl)) {
            return Promise.resolve({
                feature1: this.function1(this.url),
                feature2: this.function2(this.url),
                feature4: this.function4(this.url),
                feature5: this.function5(this.url),
                feature6: this.function6(this.url),
                feature7: this.function7(this.url),
                feature11: this.function11(this.url),
                feature12: this.function12(this.url),
            });
        }
        return fetch(this.url)
            .then(response => {
                this.response = response;
                return response.text()
            })
            .then(responseText => {
                const parser = new DOMParser();
                try {
                    this.dom = parser.parseFromString(responseText, "text/html");
                } catch (err) {
                    this.dom = null;
                }
                return Promise.resolve({
                    feature1: this.function1(this.url),
                    feature2: this.function2(this.url),
                    feature3: this.function3(this.response),
                    feature4: this.function4(this.url),
                    feature5: this.function5(this.url),
                    feature6: this.function6(this.url),
                    feature7: this.function7(this.url),
                    feature10: this.function10(this.dom, this.url),
                    feature11: this.function11(this.url),
                    feature12: this.function12(this.url),
                    feature13: this.function13(this.dom, this.url),
                    feature14: this.function14(this.dom),
                    feature15: this.function15(this.dom, this.url),
                    feature16: this.function16(this.dom, this.url),
                    feature20: this.function20(this.dom),
                    feature21: this.function21(this.dom),
                    feature22: this.function22(this.dom),
                    feature23: this.function23(this.dom),
                });
            })
            .catch(err => {
                return Promise.resolve({
                    feature1: this.function1(this.url),
                    feature2: this.function2(this.url),
                    feature4: this.function4(this.url),
                    feature5: this.function5(this.url),
                    feature6: this.function6(this.url),
                    feature7: this.function7(this.url),
                    feature11: this.function11(this.url),
                    feature12: this.function12(this.url),
                });
            });
    }
}