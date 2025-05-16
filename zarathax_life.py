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
    image_names = ["zarathax.png"]

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

def press_strong_then_hover():
    found = click_if_found("strong.png")
    hover_eye()
    time.sleep(1)
    return found

def handle_turn():
    check_for_exit()
    hover_eye()

    # 1.5: Worst case scenario — check if *any* expected cards are visible
    visible_cards = [
        "enchanted_forest.png", "strong.png", "lep.png", "lifeblade.png"
    ]
    has_cards = False

    for img in visible_cards:
        try:
            if pyautogui.locateOnScreen(f"{config.ASSET_PATH}{img}", confidence=config.CONFIDENCE):
                has_cards = True
                break
        except Exception as e:
            print(f"[⚠️] Error checking {img}: {e}")

    if not has_cards:
        print("[⚠️] No cards detected. Run likely failed. Escaping early...")
        post_battle_sequence()
        return

    if click_if_found("lifeblade.png"):
        hover_eye()
        click_first_found("kayla.png")
        return

    press_strong_then_hover()

    found_forest = click_first_found("forest.png")
    hover_eye()

    found_lep = False
    if not found_forest:
        found_lep = click_first_found("lep.png")

    hover_eye()

    if found_forest:
        click_first_found("enchanted_forest.png")
    elif found_lep:
        click_first_found("enchanted_lep.png")

    # 8. Final hover to unzoom if needed
    hover_eye()

    click_first_found("enchanted_forest.png")
    click_enemy()
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
    victory_count = 0

    while True:
        check_for_exit()
        try:
            found = pyautogui.locateOnScreen(f"{config.ASSET_PATH}flee.png", confidence=config.CONFIDENCE)
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
                    found = pyautogui.locateOnScreen(f"{config.ASSET_PATH}flee.png", confidence=config.CONFIDENCE)
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
        time.sleep(2)
        if click_if_found("quit.png"):
            break
        time.sleep(1)

    # Step 3: Wait until "play" is found and click it
    print("[▶️] Waiting for play button to appear...")
    while True:
        check_for_exit()
        time.sleep(2)
        if click_if_found("play.png"):
            time.sleep(5)
            break

    # Step 3.5: Click hub.png → then walk forward
    print("[🏙️] Waiting for hub button to appear...")
    while True:
        check_for_exit()
        try:
            if click_if_found("hub.png"):
                time.sleep(5)
                print("[🚶‍♂️] Hub clicked. Walking forward...")
                keyboard.press('up')
                time.sleep(3)
                keyboard.release('up')
                break
        except Exception as e:
            print(f"[⚠️] Error during hub lookup: {e}")
        time.sleep(1)

    # Step 3.6: Wait until hp.png is found → then click port.png
    print("[🩸] Waiting for HP bar to appear...")
    while True:
        check_for_exit()
        # try:
        #     health_visible = pyautogui.locateOnScreen(f"{config.ASSET_PATH}life_health.png", confidence=config.CONFIDENCE)
        # except pyautogui.ImageNotFoundException:
        #     health_visible = None
        # except Exception as e:
        #     print(f"[⚠️] Error checking hp.png: {e}")
        #     health_visible = None

        try:
            full_health_visible = pyautogui.locateOnScreen(f"{config.ASSET_PATH}health.png", confidence=config.CONFIDENCE)
        except pyautogui.ImageNotFoundException:
            full_health_visible = None
        except Exception as e:
            print(f"[⚠️] Error checking health.png: {e}")
            full_health_visible = None

        if full_health_visible:
            print("[📌] Health detected (partial or full). Clicking port button...")
            click_if_found("port.png")
            break

        time.sleep(3) 

    # Step 4: Wait for menu
    print("[🩺] Waiting for menu to appear...")
    while True:
        time.sleep(2)
        check_for_exit()
        try:
            menu_visible = pyautogui.locateOnScreen(f"{config.ASSET_PATH}menu.png", confidence=config.CONFIDENCE)
        except pyautogui.ImageNotFoundException:
            menu_visible = None

        if menu_visible:
            print("[~] Menu detected. Pressing 'X' key to close menu.")
            keyboard.press_and_release('x')
            time.sleep(15)
            break

        time.sleep(1)

    print("[💬] Waiting for dialogue or zara_entrance confirmation...")
    while True:
        check_for_exit()
        try:
            dialogue = pyautogui.locateOnScreen(f"{config.ASSET_PATH}dialogue.png", confidence=config.CONFIDENCE)
            if dialogue:
                print("[🗨️] Dialogue detected. Pressing space twice...")
                keyboard.press_and_release('space')
                time.sleep(0.5)
                keyboard.press_and_release('space')
                break
        except pyautogui.ImageNotFoundException:
            pass
        except Exception as e:
            print(f"[⚠️] Error checking dialogue.png: {e}")

        try:
            zara_entrance = pyautogui.locateOnScreen(f"{config.ASSET_PATH}zara_entrance.png", confidence=config.CONFIDENCE)
            if zara_entrance:
                print("[➡️] zara_entrance detected without dialogue. Proceeding...")
                break
        except pyautogui.ImageNotFoundException:
            pass
        except Exception as e:
            print(f"[⚠️] Error checking zara_entrance.png: {e}")

        time.sleep(1)

    try:
        time.sleep(3)
        dialogue = pyautogui.locateOnScreen(f"{config.ZARA_ASSET}dialogue.png", confidence=config.CONFIDENCE)
        if dialogue:
            print("[🗨️] Dialogue detected. Pressing space twice...")
            keyboard.press_and_release('space')
            time.sleep(0.5)
            keyboard.press_and_release('space')
    except pyautogui.ImageNotFoundException:
        pass
    except Exception as e:
        print(f"[⚠️] Error checking dialogue.png: {e}")
    print("[➡️] zara_entrance detected. Walking forward to reset location...")
    keyboard.press('up')
    time.sleep(7)
    keyboard.release('up')

if __name__ == "__main__":
    main()