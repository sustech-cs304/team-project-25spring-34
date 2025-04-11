from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # 获取 Chromium 的可执行路径
    chromium_path = p.chromium.executable_path
    print("Chromium 路径:", chromium_path)

    # 获取 Firefox 的可执行路径
    firefox_path = p.firefox.executable_path
    print("Firefox 路径:", firefox_path)

    # 获取 WebKit 的可执行路径
    webkit_path = p.webkit.executable_path
    print("WebKit 路径:", webkit_path)