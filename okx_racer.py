import pyautogui
import time
import easyocr
import numpy as np


def open_game() -> tuple[int, int, int, int]:
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


def click_button(okx_window: tuple[int, int, int, int], ocr: easyocr.Reader, fuel_cycles: int) -> None:
    before_price_window = (okx_window[0]+110, okx_window[1]+230, okx_window[2]-200, okx_window[3]-530)
    realtime_price_window = (okx_window[0]+196, okx_window[1]+191, okx_window[2]-310, okx_window[3]-561)

    i = 1
    while i < fuel_cycles:
        choice = "img/okx-ui/moon.png"  # TODO: AI predictions, if so - edit price comparison (line 44)
        x, y = pyautogui.locateCenterOnScreen(image=choice, confidence=0.9, region=okx_window)

        opening_price_image = np.array(pyautogui.screenshot(region=before_price_window))
        opening_price_str = ocr.recognize(opening_price_image, allowlist='0123456789,.')[0][1]
        opening_price = price_to_float(opening_price_str)

        pyautogui.click(x, y)
        time.sleep(4.75)

        current_price_image = np.array(pyautogui.screenshot(region=realtime_price_window))
        current_price_str = ocr.recognize(current_price_image, allowlist='0123456789,.')[0][1]
        current_price = price_to_float(current_price_str)

        if current_price < opening_price:
            for button in "tasks.png", "race.png":
                x, y = pyautogui.locateCenterOnScreen(image=f"img/okx-ui/{button}", confidence=0.95, region=okx_window)
                pyautogui.click(x, y)
                time.sleep(0.1)
        else:
            time.sleep(3.1)
            i += 1
    time.sleep(0.5)


def close_game():
    for button in "okx_close.png", "telegram_close.png":
        x, y = pyautogui.locateCenterOnScreen(image=f"img/close-buttons/{button}", confidence=0.95)
        pyautogui.click(x, y)


def price_to_float(price_string: str) -> float:
    return float(price_string.replace(',', ''))


def main():
    ocr = easyocr.Reader(['en'])
    fuel = 30

    refill_cycle = 1
    while True:
        print(f"{time.strftime('%H:%M:%S')} starting cycle {refill_cycle}")

        okx_window = open_game()
        pyautogui.screenshot(f"results/{refill_cycle}open.png", region=okx_window)

        click_button(okx_window, ocr, fuel)

        pyautogui.screenshot(f"results/{refill_cycle}quit.png", region=okx_window)
        close_game()

        time.sleep(2520)
        refill_cycle += 1


if __name__ == '__main__':
    main()
