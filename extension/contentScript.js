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
        } else {
            console.log(item.href);
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
        const url = item.url;
        // chrome.runtime.sendMessage({
        //     type: 0,
        //     data: url
        // }, response => {
        //    console.log(response);
        // });
        promises.push(
            new FeatureGetter(url)
                .run()
                .then(res => {
                    item.features = res;
                    console.log(url, " => ", res);
                })
                .catch(err => {
                    item.features = {};
                    console.log(url, " => ", err.message);
                })
        );
    });
    Promise.all(promises)
        .then(res => {
            console.log(tmpObj);
        })
        .catch(err => {
            console.log(err);
        })
})();

////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//// Get Features
////////////////////////////////////////////////////////////////////////////////////////////////////////////////


class FeatureGetter {

    constructor(url) {
        this.url = url;
    }

    checkIsSameOrigin(url1, url2) {
        const urlObj1 = new URL(url1);
        const urlObj2 = new URL(url2);
        return urlObj1.hostname === urlObj2.hostname;
    }

    /**
     * 如果用IP地址代替URL中的域名，如“http://125.98.3.123/fake.html”，则判断为钓鱼网站。注意：IP地址甚至转换为十六进制代码，如：http://0x58.0xCC.0xCA.0x62/2/paypal.ca/index.html
     */
    function1(url) {
        const urlObj = new URL(url);
        const slices = urlObj.hostname.split(".");
        if (slices.length !== 4)
            return 1;
        for (let i = 0; i < slices.length; i++) {
            if (isNaN(parseInt(slices[i])))
                return 1;
        }
        return -1;
    }

    /**
     * 如果URL的长度大于或等于54个字符，则该URL被归类为网络钓鱼
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
     * 短网址（http重定向） -> -1
     * 否则 -> 1
     * @param response
     */
    function3(response) {
        if (response.redirected) {
            return -1;
        }
        return 1;
    }

    /**
     * url包含@ -> -1
     * 否则 -> 1
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
     * url中最后一次出现//的位置 > 7 -> -1
     * 否则 -> 1
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
     * 域名部分包含 - 符号 -> -1
     * 否则 -> 1
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
     * url中忽略 www 和 ccTLD之后，剩余部分：
     * 包含"."的个数 <= 1 -> 1
     * 包含"."的个数 = 2 -> 0
     * 包含"."的个数 > 2 -> -1
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

    run() {
        return fetch(this.url, {
            'mode': 'no-cors'
        })
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
                });
            });
    }
}

module.exports = FeatureGetter