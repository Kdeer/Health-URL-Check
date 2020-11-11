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
    chrome.storage.sync.set({color: "#3aa757"}, () => {
        console.log("The color is green");
    })

});

