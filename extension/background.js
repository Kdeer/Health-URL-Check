chrome.runtime.onInstalled.addListener(() => {
    // Replace all rules
    chrome.declarativeContent.onPageChanged.removeRules(undefined, () => {
        // With a new rule
        chrome.declarativeContent.onPageChanged.addRules([
            {
                // The fires when a page's URL contains a
                conditions: [
                    new chrome.declarativeContent.PageStateMatcher({
                        pageUrl: {
                            schemes: ["http", "https"]
                        }
                    })
                ],
                actions: [new chrome.declarativeContent.ShowPageAction()]
            }
        ])
    })

    const url = chrome.runtime.getURL("data/security_urls.json");
    fetch(url)
        .then(response => {
            response.redirected
            return response.json();
        })
        .then(json => {
            chrome.storage.local.set(json, () => {
                console.log("save successful");
            });
        })
        .catch(err => {
            console.log(err);
        });
});