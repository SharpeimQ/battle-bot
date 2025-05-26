# Auto-install dependencies
import subprocess, sys

victory_count = 0
attempt_count = 0
conversion_count = 0
required = ["pyautogui", "keyboard", "pillow"]
for pkg in required:
    try:
        __import__(pkg)
    except ImportError:
        print(f"[📦] Installing missing package: {pkg}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

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

def if_found(image_name):
    """
    Checks if the given image exists on the screen without clicking it.
    Returns True if found, False otherwise.
    """
    check_for_exit()
    path = f"{config.ASSET_PATH}{image_name}"
    try:
        location = pyautogui.locateOnScreen(path, confidence=config.CONFIDENCE)
        if location:
            if config.VERBOSE:
                print(f"[~] Found {image_name} on screen.")
            return True
        return False
    except pyautogui.ImageNotFoundException:
        return False

def click_enemy():
    check_for_exit()
    image_names = ["goliath3.png", "enemy.png", "enemy_aura.png", "goliath.png", "goliath2.png"]

    for image_name in image_names:
        try:
            location = pyautogui.locateCenterOnScreen(
                f"{config.ASSET_PATH}{image_name}",
                confidence=config.CONFIDENCE
            )
            if location:
                pyautogui.moveTo(location)
                pyautogui.click()
                if config.VERBOSE:
                    print(f"[+] Clicked enemy using {image_name} at {location}")
                return True
            elif config.VERBOSE:
                print(f"[~] {image_name} not found.")
        except Exception as e:
            print(f"[!] Error searching for {image_name}: {e}")

    print("[!] Enemy not found using any fallback images.")
    return False

def wait_for_turn_ready():
    print(f"[~] Waiting {config.POST_CLICK_DELAY} seconds before checking for next turn...")
    time.sleep(config.POST_CLICK_DELAY)

    print("[~] Monitoring for turn readiness indicators...")

    while True:
        check_for_exit()

        # Early exit if battle has ended
        try:
            if pyautogui.locateOnScreen(f"{config.ASSET_PATH}book.png", confidence=config.CONFIDENCE):
                print("[🏆] Book detected — battle has ended.")
                return "victory"
            elif pyautogui.locateOnScreen(f"{config.ASSET_PATH}pass.png", confidence=config.CONFIDENCE) or \
                pyautogui.locateOnScreen(f"{config.ASSET_PATH}flee.png", confidence=config.CONFIDENCE):
                return "continue"
        except pyautogui.ImageNotFoundException:
            pass

        # Look for pass or flee indicators
        for indicator in ["pass.png", "flee.png"]:
            try:
                if pyautogui.locateOnScreen(f"{config.ASSET_PATH}{indicator}", confidence=config.CONFIDENCE):
                    print(f"[+] Turn is ready (detected {indicator}).")
                    return
            except pyautogui.ImageNotFoundException:
                continue

        time.sleep(1)

def hover_eye():
    try:
        location = pyautogui.locateCenterOnScreen(f"{config.ASSET_PATH}eye.png", confidence=config.CONFIDENCE)
        if location:
            pyautogui.moveTo(location)
            if config.VERBOSE:
                print(f"[~] Hovered over eye icon at {location} to reset card zoom")
            time.sleep(0.5)  # brief pause for UI to react
            return True
        else:
            if config.VERBOSE:
                print("[!] Eye icon not found on screen.")
            return False
    except pyautogui.ImageNotFoundException:
        if config.VERBOSE:
            print("[!] eye.png not detected.")
        return False
    
def press_colossal_then_hover():
    found = click_if_found("colossal.png")
    hover_eye()
    time.sleep(1)
    return found

def press_sharpen_then_hover():
    found = click_if_found("sharpen.png")
    hover_eye()
    time.sleep(1)
    return found

def press_potent_then_hover():
    found = click_if_found("potent.png")
    hover_eye()
    time.sleep(1)
    return found

def handle_turn():
    global attempt_count
    global conversion_count
    check_for_exit()

    # 1. Hover eye to reset position
    hover_eye()

    # 1.5: Worst case scenario — check for any visible card
    has_cards = False
    card_images = ["dark_pact.png", "crow.png", "enchanted_crow.png", "death_prism.png", "death_blade.png", "feint.png", "vamp.png", "enchanted_vamp.png"]

    for img in card_images:
        path = f"{config.ASSET_PATH}{img}"
        try:
            result = pyautogui.locateOnScreen(path, confidence=config.CONFIDENCE)
            if result:
                has_cards = True
                break
        except Exception as e:
            print(f"[⚠️] Error checking {img}: {e}")  # optional: remove once stable

    if not has_cards:
        attempt_count += 1
        conversion_count = 0
        print("[⚠️] No cards detected. Run likely failed. Escaping early...")
        post_battle_sequence()
        return

    if if_found("death_prism.png") and conversion_count < 1:
        click_if_found("death_prism.png")
        hover_eye()
        click_enemy()
        conversion_count += 1
        return
    
    if click_first_found("item_feint.png", "feint.png"):
        hover_eye()
        click_enemy()
        return
    
    if click_if_found("reinforce.png"):
        hover_eye()
        click_if_found("valkoor.png")
        return
    
    if click_if_found("reinforce.png"):
        hover_eye()
        click_if_found("valkoor.png")
        return

    if click_if_found("dark_pact.png"):
        hover_eye()
        click_if_found("valkoor.png")
        return
    
    if click_if_found("dark_pact.png"):
        hover_eye()
        click_if_found("valkoor.png")
        return

    # 4. Check colossal once, then hover
    press_colossal_then_hover()

    # 5. Enchant crow
    found_crow = click_first_found("crow.png")

    # 6. Enchant vamp if crow casted
    found_vamp = False
    if not found_crow:
        found_vamp = click_first_found("vamp.png")

    # 6. Hover eye (always)
    hover_eye()

    # 7. Cast Enchanted crow or second convert
    if found_crow:
        click_first_found("enchanted_crow.png")
    elif found_vamp:
        click_first_found("death_prism.png")
        hover_eye()
        click_enemy()

    # 6. Hover eye (always)
    hover_eye()
    click_first_found("enchanted_crow.png")
    hover_eye()
    click_first_found("enchanted_crow.png")
    hover_eye()
    click_first_found("enchanted_vamp.png")
    hover_eye()
    click_enemy()
    click_first_found("enchanted_vamp.png")
    hover_eye()
    click_enemy()

    # 4. Check colossal once, then hover
    # press_colossal_then_hover()
    # click_first_found("crow.png")
    # hover_eye()
    # press_colossal_then_hover()
    # click_first_found("crow.png")

    click_first_found("pass.png")


def check_for_exit():
    if keyboard.is_pressed(config.STOP_HOTKEY):
        print("[!] Exit key pressed. Terminating.")
        sys.exit(0)


def main():
    start_time = time.time()
    print("🔃 Bot is starting in idle mode.")
    print("🕒 Waiting for first battle to begin (draw button to appear)...")
    global victory_count
    global attempt_count
    victory_count = 0
    attempt_count = 0

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
        # # ⏱️ Exit after 2 hours
        # if time.time() - start_time > 2 * 60 * 60:
        #     print("[⏱️] Time limit reached. Exiting bot after 2 hours.")
        #     sys.exit(0)

        elapsed = time.time() - start_time
        elapsed_fmt = time.strftime("%H:%M:%S", time.gmtime(elapsed))
        print(f"\n=== TURN {turn} | Elapsed: {elapsed_fmt} | Victories: {victory_count} | Attempts: {attempt_count} ===")

        handle_turn()

        # Wait for the next turn or detect end of battle
        result = wait_for_turn_ready()
        
        if result == "victory":
            global conversion_count
            victory_count += 1
            attempt_count += 1
            conversion_count = 0
            print(f"[🏁] Scripted turn sequence complete. Total victories: {victory_count}: Attempts: {attempt_count}")
            post_battle_sequence()
            print("[🕒] Entering idle mode. Waiting for next battle...")

            # Loop until a new battle is detected
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
            continue
        
        # Increment turn after every cycle (safe due to stateless handle_turn)
        turn += 1


def post_battle_sequence():
    global attempt_count
    print("[🔄] Running post-battle sequence...")

    # Step 1: Open menu via ESC key instead of clicking book
    print("[⌨️] Pressing ESC to open menu...")
    keyboard.press_and_release('esc')

    # Step 2: Wait until "quit" is found and click it
    print("[🚪] Waiting for quit button to appear...")
    while True:
        check_for_exit()
        if click_if_found("quit.png"):
            break
        time.sleep(1)

    # Step 3: Wait until "play" is found and click it
    print("[▶️] Waiting for play button to appear...")
    while True:
        check_for_exit()
        if click_if_found("play.png"):
            break

    # Step 3.5: If crown shop opens (crownshop.png), close it by clicking crownshop_close.png
    print("[💰] Checking for crown shop popup over the next few seconds...")

    start_time = time.time()
    crown_closed = False

    # Step 3.5: If crown shop opens (crownshop.png), close it by pressing ESC twice
    print("[💰] Checking for crown shop popup over the next few seconds...")

    start_time = time.time()
    crown_closed = False

    while time.time() - start_time < 8:
        check_for_exit()
        try:
            shop_visible = pyautogui.locateOnScreen(f"{config.ASSET_PATH}crownshop.png", confidence=config.CONFIDENCE)
            if shop_visible:
                print("[👁️] Crown shop detected. Pressing ESC twice to close.")
                time.sleep(3)  # Give the shop time to fully load
                keyboard.press_and_release('esc')
                time.sleep(0.5)
                keyboard.press_and_release('esc')
                crown_closed = True
                break
        except pyautogui.ImageNotFoundException:
            pass
        time.sleep(1)

    if not crown_closed and config.VERBOSE:
        print("[~] Crown shop was not detected or failed to close.")

    # Step 3.75: Every 57 attempts, auto-click potion.png (no image check)
    if attempt_count > 0 and attempt_count % 57 == 0:
        print(f"[🧪] Auto potion triggered on attempt {attempt_count}...")

        click_if_found("potion.png")
        if click_if_found("potion.png"):
            print("[🍷] Potion clicked successfully.")
            time.sleep(1)
        else:
            print("[⚠️] Potion not found on screen.")

    # Step 4: Wait for both menu and hp bar to appear
    print("[🩺] Waiting for menu and hp bar to appear...")
    while True:
        check_for_exit()
        try:
            menu_visible = pyautogui.locateOnScreen(f"{config.ASSET_PATH}menu.png", confidence=config.CONFIDENCE)
        except pyautogui.ImageNotFoundException:
            menu_visible = None

        try:
            hp_visible = pyautogui.locateOnScreen(f"{config.ASSET_PATH}death_hp.png", confidence=config.CONFIDENCE)
        except pyautogui.ImageNotFoundException:
            hp_visible = None

        if menu_visible and hp_visible:
            print("[~] Menu and hp bar detected. Pressing 'X' key to close menu.")
            keyboard.press_and_release('x')
            time.sleep(15)
            break

        time.sleep(1)

    # Step 5: Wait for entrance.png to confirm spawn reset, then walk forward
    print("[🚶] Waiting for entrance confirmation...")
    while True:
        check_for_exit()
        try:
            if pyautogui.locateOnScreen(f"{config.ASSET_PATH}entrance.png", confidence=config.CONFIDENCE):
                break
        except pyautogui.ImageNotFoundException:
            pass
        time.sleep(1)

    print("[➡️] Entrance detected. Walking forward to reset location...")
    keyboard.press('up')
    time.sleep(7)
    keyboard.release('up')

if __name__ == "__main__":
    main()
