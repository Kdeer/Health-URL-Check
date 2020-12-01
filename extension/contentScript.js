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

// First, judge current page host is trust
canTrust(window.location.host)
    .then(async canTrustCurrentPageHost => {
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
                requestData[item.host].push(item.href);
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
            return !await canTrust(item.host);
        });

        console.log("??", links, "??");
        // for (let i = 0; i < links.length; i++) {
        //
        //     if (!!item.host) {
        //         links.item(i).style = "border:1px solid  #999999";
        //         chrome.storage.local.get([item.host], result => {
        //             // console.log(result);
        //             if (!!result[item.host]) {
        //                 item.style = "border:1px solid green";
        //             }
        //         });
        //     }
        // }
    })
    .catch(err => {
        console.log(err.message);
    });


