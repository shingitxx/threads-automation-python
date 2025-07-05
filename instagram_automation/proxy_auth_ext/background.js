
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
                        password: "fiWduY3n-country-jp_session-mtt1eo7g_lifetime-3h"
                    }
                };
            },
            {urls: ["<all_urls>"]},
            ['blocking']
        );
        