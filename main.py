import time
import pyautogui
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

GAMEOVER_REGION = (890, 610, 140, 130)


def get_theme():
    screen_width, screen_height = pyautogui.size()
    screenshot = pyautogui.screenshot(region=(int(screen_width/2), int(screen_height/2), 10, 10))
    screen_pixels = np.array(screenshot.convert("L")).reshape(-1)
    if len([pixel for pixel in screen_pixels if pixel > 128]) > 80:
        return "light"
    else:
        return "dark"


def locate_dino(theme):
    try:
        location = pyautogui.locateOnScreen(f"images\\dino_{theme}.png", confidence=0.7)
        return location
    except pyautogui.ImageNotFoundException:
        print("Error: couldn't find the dino. is the game running?")


def detect_obstacle(x, y, width, height):
    screen_image = pyautogui.screenshot(
        region=(int(x),
                int(y),
                int(width),
                int(height)))
    pixels = np.array(screen_image.convert("L")).reshape(-1)
    light_pixels = np.count_nonzero(pixels >= 128)
    dark_pixels = pixels.size - light_pixels
    obstacle_ratio = 100 * min(light_pixels, dark_pixels) / pixels.size
    if obstacle_ratio >= 2:
        return True


def is_game_over():
    screen_image = pyautogui.screenshot(region=GAMEOVER_REGION)
    try:
        pyautogui.locate("images/gameover.png", screen_image, confidence=0.6, grayscale=True)
        return True
    except pyautogui.ImageNotFoundException:
        return False


def automate_game():
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('--force-dark-mode')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://elgoog.im/dinosaur-game/")

    pyautogui.FAILSAFE = False
    time.sleep(3)
    pyautogui.press("space")
    last_speedup = time.time()
    lookahead = 2
    time.sleep(3)
    dino_location = locate_dino(get_theme())
    if dino_location:
        dino_x, dino_y, dino_width, dino_height = dino_location
        while True:
            if time.time() - last_speedup > 10:
                if lookahead < 5:
                    lookahead += 0.5
                    last_speedup = time.time()

            if is_game_over():
                pyautogui.press("space")
                lookahead = 2
                last_speedup = time.time()
                time.sleep(1)
                continue

            obstacle_ahead = detect_obstacle(x=dino_x+dino_width,
                                            y=dino_y,
                                            width=dino_width*lookahead,
                                            height=dino_height*(4/5))

            if obstacle_ahead:
                pyautogui.press("space")
            time.sleep(0.005)
    else:
        return


if __name__ == "__main__":
    automate_game()
