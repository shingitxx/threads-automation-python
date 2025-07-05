import zipfile
import os

def create_proxy_auth_extension(proxy_host, proxy_port, proxy_user, proxy_pass, scheme='http'):
    """プロキシ認証用のChrome拡張機能を作成"""
    
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = f"""
    var config = {{
        mode: "fixed_servers",
        rules: {{
            singleProxy: {{
                scheme: "{scheme}",
                host: "{proxy_host}",
                port: parseInt({proxy_port})
            }},
            bypassList: ["localhost"]
        }}
    }};

    chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

    function callbackFn(details) {{
        return {{
            authCredentials: {{
                username: "{proxy_user}",
                password: "{proxy_pass}"
            }}
        }};
    }}

    chrome.webRequest.onAuthRequired.addListener(
        callbackFn,
        {{urls: ["<all_urls>"]}},
        ['blocking']
    );
    """

    extension_dir = "proxy_auth_extension"
    
    if not os.path.exists(extension_dir):
        os.makedirs(extension_dir)
    
    with open(f"{extension_dir}/manifest.json", 'w') as f:
        f.write(manifest_json)
    
    with open(f"{extension_dir}/background.js", 'w') as f:
        f.write(background_js)
    
    # ZIP化
    extension_path = f"{extension_dir}.zip"
    with zipfile.ZipFile(extension_path, 'w') as zp:
        zp.write(f"{extension_dir}/manifest.json", "manifest.json")
        zp.write(f"{extension_dir}/background.js", "background.js")
    
    return extension_path

# 使用例
if __name__ == "__main__":
    # IPRoyalの情報
    sessions = ["w0sc3hsf_lifetime-2h"]
    selected_session = sessions[0]
    
    extension_path = create_proxy_auth_extension(
        proxy_host="iproyal-aisa.hellworld.io",
        proxy_port="12322",
        proxy_user="C9kNyNmY",
        proxy_pass=f"fiWduY3n-country-jp_session-{selected_session}"
    )
    
    print(f"✅ プロキシ拡張機能を作成しました: {extension_path}")