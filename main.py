import time
import glob
import pyautogui
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

DARK_OBSTACLES = [Image.open(img) for img in glob.glob("images\\obstacles\\dark\\" + "*")]
LIGHT_OBSTACLES = [Image.open(img) for img in glob.glob("images\\obstacles\\light\\" + "*")]
BACKGROUND = {"light": LIGHT_OBSTACLES, "dark": DARK_OBSTACLES}

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument('--force-dark-mode')
driver = webdriver.Chrome(options=chrome_options)
driver.get("https://elgoog.im/dinosaur-game/")


def get_bg_color(driver):
    try:
        driver.find_element(By.CLASS_NAME, "g-dark")
        return "dark"
    except NoSuchElementException:
        return "light"


time.sleep(2)
pyautogui.press("space")
coef_start = time.time()
coef = 2
time.sleep(3)

bg_color = get_bg_color(driver)
dino_x, dino_y, dino_width, dino_height = pyautogui.locateOnScreen(f"images\\dino_{bg_color}.png", confidence=0.7)

while True:
    bg_color = get_bg_color(driver)
    # Every 10 seconds increase the detection range as the game speed increases.
    # A larger coefficient lets the bot detect obstacles farther ahead.
    if time.time() - coef_start > 10:
        if coef == 3:
            coef += 1
            coef_start = time.time()
        elif coef < 6:
            coef += 0.5
            coef_start = time.time()

    screen_image = pyautogui.screenshot(
        region=(int(dino_x + dino_width),
                int(dino_y),
                int(dino_width*coef),
                int(dino_height*1.5)))
    
    for obstacle in BACKGROUND[bg_color]:
        try:
            pyautogui.locate(
                needleImage=obstacle,
                haystackImage=screen_image,
                confidence=0.5,
                grayscale=True)
            pyautogui.press("space")
            break
        except pyautogui.ImageNotFoundException:
            continue
