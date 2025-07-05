
    var config = {
        mode: "fixed_servers",
        rules: {
            singleProxy: {
                scheme: "http",
                host: "pr.smtproxies.com",
                port: parseInt(7777)
            },
            bypassList: ["localhost"]
        }
    };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    chrome.webRequest.onAuthRequired.addListener(
        function(details) {
            console.log('Authentication for: ' + details.url);
            return {
                authCredentials: {
                    username: "customer-SR001pgFWbvMXm-cc-JP-sessid-smt3312550677",
                    password: "SMT011+xtkWUziE9W"
                }
            };
        },
        {urls: ["<all_urls>"]},
        ['blocking']
    );

    chrome.webRequest.onBeforeRequest.addListener(
        function(details) {
            console.log('Request: ' + details.url);
            return {cancel: false};
        },
        {urls: ["<all_urls>"]}
    );
    