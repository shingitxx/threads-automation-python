
        var config = {
            mode: "fixed_servers",
            rules: {
                singleProxy: {
                    scheme: "http",
                    host: "pr.smtproxies.com",
                    port: parseInt(7777)
                },
                bypassList: ["localhost", "127.0.0.1"]
            }
        };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "customer-SR001pgFWbvMXm-cc-JP-sessid-smt3291084715",
                    password: "SMT011+xtkWUziE9W"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
        );
        