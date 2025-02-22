# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "playwright",
# ]
# ///
from playwright.sync_api import sync_playwright, Route, Page, Playwright
import json
from bisect import bisect
from operator import itemgetter

PRICE_DATA: list[dict] = []

def framereceived_handler(payload: str) -> None:
    """Collect websocket price data"""
    payload = json.loads(payload)
    if payload.get("event") is None:
        payload_data = payload["data"][0]
        price_and_timestamp = {
            "last": float(payload_data["last"]),
            "ts": int(payload_data["ts"])
        }
        PRICE_DATA.append(price_and_timestamp)

def assess_router(route: Route) -> None:
    """Modify main request based on collected websocket data"""
    present_ts = int(route.request.url[-13:])
    past_ts = present_ts - (5 * 1000)
    past_index = bisect(PRICE_DATA, past_ts, key=itemgetter("ts"))
    past_price = PRICE_DATA[past_index]["last"]
    present_price = PRICE_DATA[-1]["last"]
    # post_data = '{"predict":1}' if present_price >= past_price else '{"predict":0}'
    # route.continue_(post_data=post_data)
    route.continue_() if present_price >= past_price else route.abort()
    del PRICE_DATA[:past_index]

def setup_page(page: Page) -> None:
    page.route("**/assess?t=*", assess_router)
    page.on("websocket", lambda ws: ws.on("framereceived", framereceived_handler))
    page.reload()

def use_fuel(page: Page) -> None:
    moon_el = page.get_by_role("button", name="MOON")
    fuel_el = page.get_by_text("/ 28")
    while fuel_el.inner_text().split(' / ')[0] != '0':
        moon_el.click()
        page.wait_for_timeout(7500)

def goto_reload_page(page: Page) -> None:
    page.get_by_role("link", name="Upgrades").click()
    page.get_by_text("Car", exact=True).click()

def reload_fuel(page: Page) -> None:
    page.get_by_role("button", name="Reload Fuel Tank").click()
    page.get_by_role("button", name="Boost Now").click()
    page.get_by_label("Close").click()
    page.go_back()

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
    page = browser.contexts[0].pages[0]
    setup_page(page)
    while True:
        use_fuel(page)
        goto_reload_page(page)
        if page.get_by_text("/3").inner_text()[0] == '0':
            break
        reload_fuel(page)

if __name__ == "__main__":
    with sync_playwright() as p:
        run(p)
