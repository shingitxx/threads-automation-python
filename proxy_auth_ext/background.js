
        var config = {
            mode: "fixed_servers",
            rules: {
                singleProxy: {
                    scheme: "http",
                    host: "iproyal-aisa.hellworld.io",
                    port: parseInt(12322)
                },
                bypassList: ["localhost"]
            }
        };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        chrome.webRequest.onAuthRequired.addListener(
            function(details) {
                return {
                    authCredentials: {
                        username: "C9kNyNmY",
                        password: "fiWduY3n-country-jp_session-pr.smtproxies.com:7777:customer-SR001pgFWbvMXm-cc-JP-sessid-smt2222703370:SMT011+xtkWUziE9W"
                    }
                };
            },
            {urls: ["<all_urls>"]},
            ['blocking']
        );
        