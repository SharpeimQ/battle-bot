import pyautogui
import time
import keyboard
import config
import sys

pyautogui.FAILSAFE = True

def click_if_found(image_name, clicks=1, delay=0.5):
    check_for_exit()
    path = f"{config.ASSET_PATH}{image_name}"
    try:
        location = pyautogui.locateOnScreen(path, confidence=config.CONFIDENCE)
        if location:
            center_x = location.left + location.width // 2
            center_y = location.top + location.height // 2
            pyautogui.moveTo(center_x, center_y)
            for _ in range(clicks):
                pyautogui.click()
                time.sleep(delay)
            if config.VERBOSE:
                print(f"[+] Clicked {image_name} at ({center_x}, {center_y})")
            return True
        return False
    except pyautogui.ImageNotFoundException:
        if config.VERBOSE:
            print(f"[!] Image not found: {image_name}")
        return False

def click_first_found(*image_names):
    for name in image_names:
        if click_if_found(name):
            return True
    return False

def click_enemy():
    check_for_exit()
    try:
        location = pyautogui.locateCenterOnScreen(
            f"{config.ASSET_PATH}enemy.png",
            confidence=config.CONFIDENCE
        )
        if location:
            pyautogui.moveTo(location)
            pyautogui.click()
            if config.VERBOSE:
                print(f"[+] Clicked enemy at {location}")
            return True
        else:
            if config.VERBOSE:
                print("[!] Enemy not found on screen.")
            return False
    except Exception as e:
        print(f"[!] Error locating enemy: {e}")
        return False

def wait_for_turn_ready():
    print(f"[~] Waiting {config.POST_CLICK_DELAY} seconds before checking for next turn...")
    time.sleep(config.POST_CLICK_DELAY)

    start = time.time()
    while True:
        check_for_exit()
        try:
            found = pyautogui.locateOnScreen(
                f"{config.ASSET_PATH}draw_button.png",
                confidence=config.CONFIDENCE
            )
        except pyautogui.ImageNotFoundException:
            found = None

        if found:
            print("[+] Turn is ready.")
            return

        if keyboard.is_pressed(config.STOP_HOTKEY):
            print("[!] Aborted by user.")
            exit()

        if time.time() - start > config.TURN_TIMEOUT:
            print("[!] Timeout waiting for turn.")
            return

        time.sleep(1)

def click_pet():
    try:
        location = pyautogui.locateCenterOnScreen(f"{config.ASSET_PATH}pet.png", confidence=config.CONFIDENCE)
        if location:
            pyautogui.moveTo(location)
            pyautogui.click()
            if config.VERBOSE:
                print(f"[~] Clicked pet at {location} to reset zoom")
            time.sleep(0.5)
            return True
        else:
            print("[!] Pet not found.")
            return False
    except pyautogui.ImageNotFoundException:
        print("[!] Pet image not found at all.")
        return False


def check_for_exit():
    if keyboard.is_pressed(config.STOP_HOTKEY):
        print("[!] Exit key pressed. Terminating.")
        sys.exit(0)


def main():
    print("🔃 Bot is starting in idle mode.")
    print("🕒 Waiting for first battle to begin (draw button to appear)...")

    while True:
        check_for_exit()
        try:
            found = pyautogui.locateOnScreen(f"{config.ASSET_PATH}draw_button.png", confidence=config.CONFIDENCE)
        except pyautogui.ImageNotFoundException:
            found = None

        if found:
            print("[⚔️] Battle detected. Starting turn logic...")
            break

        time.sleep(1)

    keyboard.add_hotkey(config.STOP_HOTKEY, lambda: sys.exit("[!] Exit key pressed. Exiting..."))
    turn = 1

    while True:
        check_for_exit()
        print(f"\n=== TURN {turn} ===")

        if turn == 1:
            click_if_found("draw_button.png")
            time.sleep(2.5)
            click_if_found("darkwind.png")
            click_pet()

        elif turn == 2:
            click_if_found("galvanic.png")
            click_pet()

        elif turn == 3:
            if not click_if_found("colossal.png"):
                print("[!] Colossal not found. Moving to player and retrying...")
                click_pet()
                time.sleep(1)
                if not click_if_found("colossal.png"):
                    print("[✖] Still not found. Skipping Turn 3.")
                    continue

            time.sleep(3)
            click_pet()
            check_for_exit()

            if not click_first_found("stormlord.png", "scaled_stormlord.png", "semi_stormlord.png"):
                print("[!] Storm Lord not found. Moving to player and retrying...")
                click_pet()
                time.sleep(1)
                if not click_first_found("stormlord.png", "scaled_stormlord.png", "semi_stormlord.png"):
                    print("[✖] Still not found. Skipping Turn 3.")
                    continue

            time.sleep(3)
            click_pet()
            check_for_exit()

            if not click_first_found("enchanted_stormlord.png", "scaled_enchanted_stormlord.png", "semi_enchanted_stormlord.png"):
                print("[!] Enchanted Storm Lord not found. Moving to player and retrying...")
                click_pet()
                time.sleep(1)
                click_first_found("enchanted_stormlord.png", "scaled_enchanted_stormlord.png", "semi_enchanted_stormlord.png")

        elif turn == 4:
            if not click_if_found("colossal.png"):
                print("[!] Colossal not found. Moving to player and retrying...")
                click_pet()
                time.sleep(1)
                if not click_if_found("colossal.png"):
                    print("[✖] Still not found. Skipping Turn 4.")
                    continue

            time.sleep(3)
            click_pet()
            check_for_exit()

            if not click_first_found("bats.png", "scaled_bats.png", "semi_bats.png"):
                print("[!] Bats not found. Moving to player and retrying...")
                click_pet()
                time.sleep(1)
                if not click_first_found("bats.png", "scaled_bats.png", "semi_bats.png"):
                    print("[✖] Still not found. Skipping Turn 4.")
                    continue

            time.sleep(3)
            click_pet()
            check_for_exit()

            if not click_first_found("enchanted_bats.png", "semi_enchanted_bats.png"):
                print("[!] Enchanted Bats not found. Moving to player and retrying...")
                click_pet()
                time.sleep(1)
                if not click_first_found("enchanted_bats.png", "semi_enchanted_bats.png"):
                    print("[✖] Still not found. Skipping Turn 4.")
                    continue

            time.sleep(3)
            click_pet()
            click_enemy()

        elif turn == 5:
            if click_first_found("bats.png", "scaled_bats.png", "enchanted_bats.png"):
                click_enemy()
            else:
                print("[!] No bats found. Ending early.")

            print("[🏁] Scripted turn sequence complete.")
            print("[🕒] Entering idle mode. Waiting for next battle...")

            while True:
                check_for_exit()
                try:
                    found = pyautogui.locateOnScreen(f"{config.ASSET_PATH}draw_button.png", confidence=config.CONFIDENCE)
                except pyautogui.ImageNotFoundException:
                    found = None

                if found:
                    print("[⚔️] New battle detected. Restarting turn logic...")
                    turn = 1
                    break

                time.sleep(1)

        time.sleep(config.POST_CLICK_DELAY)
        wait_for_turn_ready()
        turn += 1


if __name__ == "__main__":
    main()
