import pyautogui
import time
import easyocr
import numpy as np


type Region = tuple[int, int, int, int]


def open_game() -> Region:
    for button in "telegram.png", "okx_chat.png", "play.png":
        x, y = pyautogui.locateCenterOnScreen(image=f"img/open-buttons/{button}", confidence=0.95)
        pyautogui.click(x, y)
        time.sleep(0.5)
    time.sleep(2)
    try:
        x, y = pyautogui.locateCenterOnScreen(image="img/okx-ui/continue_button.png", confidence=0.95)
        pyautogui.click(x, y)
        time.sleep(0.5)
    except pyautogui.ImageNotFoundException:
        pass
    finally:
        okx_window = pyautogui.locateOnScreen(image="img/okx-ui/okx_window.png", confidence=0.6)
        return okx_window[0].item(), okx_window[1].item(), okx_window[2], okx_window[3]


def click_button(okx_window: Region, ocr: easyocr.Reader, fuel_cycles: int) -> None:
    print(f"{time.strftime('%H:%M:%S')} started clicking cycle")
    before_price_window = (okx_window[0]+110, okx_window[1]+215, okx_window[2]-200, okx_window[3]-530)
    realtime_price_window = (okx_window[0]+198, okx_window[1]+175, okx_window[2]-310, okx_window[3]-560)

    i = 1
    while i < fuel_cycles:
        choice = "img/okx-ui/moon.png"  # TODO: AI predictions, if so - edit price comparison (line 44)
        x, y = pyautogui.locateCenterOnScreen(image=choice, confidence=0.9, region=okx_window)

        opening_price = get_price(before_price_window, ocr)

        pyautogui.click(x, y)
        time.sleep(4.75)

        current_price = get_price(realtime_price_window, ocr)

        if current_price < opening_price:
            for button in "tasks.png", "race.png":
                x, y = pyautogui.locateCenterOnScreen(image=f"img/okx-ui/{button}", confidence=0.95, region=okx_window)
                pyautogui.click(x, y)
                time.sleep(0.1)
        else:
            time.sleep(3.1)
            i += 1
    time.sleep(0.5)


def refill_fuel(okx_window: Region) -> None:
    print(f"{time.strftime('%H:%M:%S')} started refilling")
    for button in "tasks.png", "refill.png", "refill_confirm.png", "race.png":
        x, y = pyautogui.locateCenterOnScreen(image=f"img/okx-ui/{button}", confidence=0.95, region=okx_window)
        pyautogui.click(x, y)
        time.sleep(0.8)


def close_game() -> None:
    for button in "okx_close.png", "telegram_close.png":
        x, y = pyautogui.locateCenterOnScreen(image=f"img/close-buttons/{button}", confidence=0.95)
        pyautogui.click(x, y)


def get_price(region: Region, ocr: easyocr.Reader) -> float:
    price_image = np.array(pyautogui.screenshot(region=region))
    price_str = ocr.recognize(price_image, allowlist='0123456789,.')[0][1]
    return float(price_str.replace(',', ''))


def main() -> None:
    ocr = easyocr.Reader(['en'])
    fuel = 30
    refill_available = 3

    okx_window = open_game()
    click_button(okx_window, ocr, fuel)
    for i in range(refill_available):
        refill_fuel(okx_window)
        click_button(okx_window, ocr, fuel)
    close_game()


if __name__ == '__main__':
    main()
