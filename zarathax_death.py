# 1. deathblade1.png -> valkoor
# 2. deathblade2.png -> valkoor
# 3. deathblade3.png -> valkoor
# 4. feint -> zarathrax
# 5. enchant -> ship
# 5a. cast enchanted_ship

# Auto-install dependencies
import subprocess, sys

victory_count = 0
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
    path = f"{config.ZARA_ASSET}{image_name}"
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
    image_names = ["zarathax.png", "merc.png"]

    for image_name in image_names:
        try:
            location = pyautogui.locateCenterOnScreen(
                f"{config.ZARA_ASSET}{image_name}",
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
            if pyautogui.locateOnScreen(f"{config.ZARA_ASSET}book.png", confidence=config.CONFIDENCE):
                print("[🏆] Book detected — battle has ended.")
                return "victory"
            elif pyautogui.locateOnScreen(f"{config.ZARA_ASSET}pass.png", confidence=config.CONFIDENCE) or \
                pyautogui.locateOnScreen(f"{config.ZARA_ASSET}flee.png", confidence=config.CONFIDENCE):
                return "continue"
        except pyautogui.ImageNotFoundException:
            pass

        # Look for pass or flee indicators
        for indicator in ["pass.png", "flee.png"]:
            try:
                if pyautogui.locateOnScreen(f"{config.ZARA_ASSET}{indicator}", confidence=config.CONFIDENCE):
                    print(f"[+] Turn is ready (detected {indicator}).")
                    return
            except pyautogui.ImageNotFoundException:
                continue

        time.sleep(1)

def hover_eye():
    try:
        location = pyautogui.locateCenterOnScreen(f"{config.ZARA_ASSET}eye.png", confidence=config.CONFIDENCE)
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
    
# def press_colossal_then_hover():
#     found = click_if_found("colossal.png")
#     hover_eye()
#     time.sleep(1)
#     return found

def press_strong_then_hover():
    found = click_if_found("strong.png")
    hover_eye()
    time.sleep(1)
    return found


def handle_turn():
    check_for_exit()

    # 1. Hover eye to reset zoom
    hover_eye()

    # 1.5: Worst case scenario — check for any visible card
    has_cards = False
    card_images = [
        "deathblade1.png", "deathblade2.png", "deathblade3.png",
        "feint.png", "strong.png", "enchanted_ship.png", "enchanted_vampire.png", "vampire.png"
    ]

    for img in card_images:
        path = f"{config.ZARA_ASSET}{img}"
        try:
            result = pyautogui.locateOnScreen(path, confidence=config.CONFIDENCE)
            if result:
                has_cards = True
                break
        except Exception as e:
            print(f"[⚠️] Error checking {img}: {e}")

    if not has_cards:
        print("[⚠️] No cards detected. Run likely failed. Escaping early...")
        post_battle_sequence()
        return

    # 2. Check deathblades → valkoor
    if click_if_found("deathblade1.png"):
        hover_eye()
        click_if_found("valkoor.png")
        return

    # if click_if_found("deathblade2.png"):
    #     hover_eye()
    #     click_if_found("valkoor.png")
    #     return

    if click_if_found("deathblade3.png"):
        hover_eye()
        click_if_found("valkoor.png")
        return

    # 3. Check feint → zarathrax
    if click_if_found("feint.png"):
        hover_eye()
        click_if_found("zarathax.png")
        return

    # 4. Check colossal once, then hover
    press_strong_then_hover()

    # 5. Enchant Ship
    found_ship = click_first_found("ship.png")

    # 6. Enchant Vampire if Ship casted
    found_vampire = False
    if not found_ship:
        found_vampire = click_first_found("vampire.png")

    # 6. Hover eye (always)
    hover_eye()

    click_first_found("enchanted_ship.png")
    # 7. Cast Enchanted Ship or Vampire
    if found_ship:
        click_first_found("enchanted_ship.png")
    elif found_vampire:
        click_first_found("enchanted_vampire.png")

    # 8. Final hover to unzoom if needed
    hover_eye()

    # Final enemy click for Enchanted Vampire
    click_enemy()


def check_for_exit():
    if keyboard.is_pressed(config.STOP_HOTKEY):
        print("[!] Exit key pressed. Terminating.")
        sys.exit(0)


def main():
    start_time = time.time()
    print("🔃 Bot is starting in idle mode.")
    print("🕒 Waiting for first battle to begin (draw button to appear)...")
    global victory_count
    victory_count = 0

    while True:
        check_for_exit()
        try:
            found = pyautogui.locateOnScreen(f"{config.ZARA_ASSET}flee.png", confidence=config.CONFIDENCE)
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
        # ⏱️ Exit after 2 hours
        if time.time() - start_time > 2 * 60 * 60:
            print("[⏱️] Time limit reached. Exiting bot after 2 hours.")
            sys.exit(0)

        elapsed = time.time() - start_time
        elapsed_fmt = time.strftime("%H:%M:%S", time.gmtime(elapsed))
        spells = victory_count * 14
        print(f"\n=== TURN {turn} | Elapsed: {elapsed_fmt} | Victories: {victory_count} | Spells: {spells} ===")

        handle_turn()

        # Wait for the next turn or detect end of battle
        result = wait_for_turn_ready()
        
        if result == "victory":
            victory_count += 1
            print(f"[🏁] Scripted turn sequence complete. Total victories: {victory_count}")
            post_battle_sequence()
            print("[🕒] Entering idle mode. Waiting for next battle...")

            # Loop until a new battle is detected
            while True:
                check_for_exit()
                try:
                    found = pyautogui.locateOnScreen(f"{config.ZARA_ASSET}flee.png", confidence=config.CONFIDENCE)
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
        time.sleep(2)

    # Step 3: Wait until "play" is found and click it
    print("[▶️] Waiting for play button to appear...")
    while True:
        check_for_exit()
        if click_if_found("play.png"):
            break
        time.sleep(5)

    # Step 3.5: Check for low mana and click potion if needed
    print("[🧪] Checking for low mana...")
    try:
        low_mana = pyautogui.locateOnScreen(f"{config.ZARA_ASSET}low_mana.png", confidence=config.CONFIDENCE)
        if low_mana:
            print("[🔋] Low mana detected. Clicking potion...")
            click_if_found("potion.png")
            time.sleep(1)
    except Exception as e:
        print(f"[⚠️] Error checking low_mana.png: {e}")

    # Step 4: Wait for both menu and hp bar to appear
    print("[🩺] Waiting for menu and hp bar to appear...")
    while True:
        check_for_exit()
        try:
            menu_visible = pyautogui.locateOnScreen(f"{config.ZARA_ASSET}menu.png", confidence=config.CONFIDENCE)
        except pyautogui.ImageNotFoundException:
            menu_visible = None

        try:
            hp_visible = pyautogui.locateOnScreen(f"{config.ZARA_ASSET}hp.png", confidence=config.CONFIDENCE)
        except pyautogui.ImageNotFoundException:
            hp_visible = None

        if menu_visible and hp_visible:
            print("[~] Menu and hp bar detected. Pressing 'X' key to close menu.")
            keyboard.press_and_release('x')
            time.sleep(15)
            break

        time.sleep(1)

    # Step 4.5: Wait for dialogue.png to appear, then press space twice
    print("[💬] Waiting for dialogue to appear...")
    while True:
        check_for_exit()
        try:
            dialogue = pyautogui.locateOnScreen(f"{config.ZARA_ASSET}dialogue.png", confidence=config.CONFIDENCE)
            if dialogue:
                print("[📖] Dialogue detected. Pressing space twice...")
                keyboard.press_and_release('space')
                time.sleep(0.5)
                keyboard.press_and_release('space')
                break
        except Exception as e:
            print(f"[⚠️] Error checking dialogue.png: {e}")
        time.sleep(1)

    # Step 5: Wait for entrance.png to confirm spawn reset, then walk forward
    print("[🚶] Waiting for entrance confirmation...")
    while True:
        check_for_exit()
        try:
            if pyautogui.locateOnScreen(f"{config.ZARA_ASSET}entrance.png", confidence=config.CONFIDENCE):
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
