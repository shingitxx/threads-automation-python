import requests

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.1secmail.com/',
}

TEST_LOGIN = "test"
TEST_DOMAIN = "1secmail.com"
URL = f"https://www.1secmail.com/api/v1/?action=getMessages&login={TEST_LOGIN}&domain={TEST_DOMAIN}"

def test_proxy(proxy):
    try:
        proxies = {
            "http": proxy,
            "https": proxy
        }
        response = requests.get(URL, headers=HEADERS, proxies=proxies, timeout=10)
        if response.status_code == 200 and response.text.startswith("[") or response.text.startswith("{"):
            return True
        else:
            print(f"[✖] {proxy} → {response.status_code}: {response.text[:50]}")
            return False
    except Exception as e:
        print(f"[✖] {proxy} → Error: {str(e)}")
        return False

def main():
    try:
        with open("proxies.txt", "r") as f:
            proxies = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("⚠️ proxies.txt ファイルが見つかりません。ファイルを同じフォルダに用意してください。")
        return

    working_proxies = []
    print(f"[INFO] 総プロキシ数: {len(proxies)}")

    for proxy in proxies:
        print(f"[...] テスト中: {proxy}")
        if test_proxy(proxy):
            print(f"[✔] 使用可能: {proxy}")
            working_proxies.append(proxy)

    print(f"\n✅ 使用可能なプロキシ一覧（{len(working_proxies)}本）:")
    for wp in working_proxies:
        print(wp)

    with open("working_proxies.txt", "w") as f:
        f.write("\n".join(working_proxies))

if __name__ == "__main__":
    main()
