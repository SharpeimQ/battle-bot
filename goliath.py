# Auto-install dependencies
import subprocess, sys

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

def check_for_exit():
    if keyboard.is_pressed(config.STOP_HOTKEY):
        print("[!] Exit key pressed. Terminating.")
        sys.exit(0)


def main():
    start_time = time.time()
    print("🔃 Bot is starting in idle mode.")
    print("🕒 Waiting for first battle to begin (draw button to appear)...")

    while True:
        # ⏱️ Exit after 2 hours
        if time.time() - start_time > 2 * 60 * 60:
            print("[⏱️] Time limit reached. Exiting bot after 2 hours.")
            sys.exit(0)

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
        hover_eye()
        print(f"\n=== TURN {turn} ===")

        if turn == 1:
            for attempt in range(5):
                if click_if_found("draw_button.png"):
                    break
                print(f"[{attempt+1}/5] draw_button.png not found. Retrying in 1.5s...")
                time.sleep(1.5)

            time.sleep(3)

            for attempt in range(5):
                if click_if_found("darkwind.png"):
                    break
                print(f"[{attempt+1}/5] darkwind.png not found. Retrying in 1.5s...")
                time.sleep(1.5)

        elif turn == 2:
            click_if_found("darkwind.png")

            for attempt in range(5):
                if click_if_found("galvanic.png"):
                    break
                print(f"[{attempt+1}/5] galvanic.png not found. Retrying in 1.5s...")
                time.sleep(1.5)


        elif turn == 3:
            click_if_found("darkwind.png")
            click_if_found("galvanic.png")

            success = False
            for attempt in range(10):
                if press_colossal_then_hover():
                    success = True
                    break
                print(f"[{attempt+1}/10] Colossal not found. Retrying in 2s...")
                time.sleep(2)
            if not success:
                print("[✖] Colossal not found after 10 tries. Skipping Turn 3.")
                continue

            check_for_exit()

            if not click_first_found("stormlord.png", "scaled_stormlord.png", "semi_stormlord.png"):
                print("[!] Storm Lord not found. Moving to player and retrying...")
                hover_eye()
                time.sleep(1)
                if not click_first_found("stormlord.png", "scaled_stormlord.png", "semi_stormlord.png"):
                    print("[✖] Still not found. Skipping Turn 3.")
                    continue

            time.sleep(3)
            check_for_exit()

            if not click_first_found("enchanted_stormlord.png", "scaled_enchanted_stormlord.png", "semi_enchanted_stormlord.png"):
                print("[!] Enchanted Storm Lord not found. Moving to player and retrying...")
                hover_eye()
                time.sleep(1)
                click_first_found("enchanted_stormlord.png", "scaled_enchanted_stormlord.png", "semi_enchanted_stormlord.png")


        elif turn == 4:
            click_if_found("darkwind.png")
            click_if_found("galvanic.png")
        
            success = False
            for attempt in range(10):
                if press_colossal_then_hover():
                    success = True
                    break
                print(f"[{attempt+1}/10] Colossal not found. Retrying in 2s...")
                time.sleep(2)
            if not success:
                print("[✖] Colossal not found after 10 tries. Skipping Turn 4.")
                continue

            check_for_exit()

            if not click_first_found("bats.png", "scaled_bats.png", "semi_bats.png"):
                print("[!] Bats not found. Moving to player and retrying...")
                hover_eye()
                time.sleep(1)
                if not click_first_found("bats.png", "scaled_bats.png", "semi_bats.png"):
                    print("[✖] Still not found. Skipping Turn 4.")
                    continue

            time.sleep(3)
            check_for_exit()

            if not click_first_found("enchanted_bats.png", "semi_enchanted_bats.png"):
                print("[!] Enchanted Bats not found. Moving to player and retrying...")
                hover_eye()
                time.sleep(1)
                if not click_first_found("enchanted_bats.png", "semi_enchanted_bats.png"):
                    print("[✖] Still not found. Skipping Turn 4.")
                    continue

            click_enemy()

        elif turn == 5:
            victory_detected = False

            try:
                if pyautogui.locateOnScreen(f"{config.ASSET_PATH}book.png", confidence=config.CONFIDENCE):
                    print("[🏆] Victory detected early (book visible).")
                    victory_detected = True
            except pyautogui.ImageNotFoundException:
                pass

            if not victory_detected:
                hover_eye()
                if click_first_found("bats.png", "scaled_bats.png", "enchanted_bats.png"):
                    click_enemy()
                    time.sleep(10)
                else:
                    print("[!] No bats found. Ending early.")
            
            print("[🏁] Scripted turn sequence complete.")
            post_battle_sequence()

            # Shared idle loop
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
            continue


        time.sleep(config.POST_CLICK_DELAY)
        wait_for_turn_ready()
        # Only increment turn if not reset
        if turn < 5:
            turn += 1


def post_battle_sequence():
    print("[🔄] Running post-battle sequence...")

    # Step 1: Open menu via ESC key instead of clicking book
    print("[⌨️] Pressing ESC to open menu...")
    keyboard.press_and_release('esc')
    time.sleep(5)

    # Step 2: Click quit
    if click_if_found("quit.png"):
        time.sleep(10)

        # Step 3: Click play
        if click_if_found("play.png"):
            print("[🩺] Waiting for menu and health bar to appear...")
            
            # Step 4: Wait indefinitely until both menu and health bar are detected
            while True:
                check_for_exit()

                try:
                    menu_visible = pyautogui.locateOnScreen(f"{config.ASSET_PATH}menu.png", confidence=config.CONFIDENCE)
                except pyautogui.ImageNotFoundException:
                    menu_visible = None

                try:
                    health_visible = pyautogui.locateOnScreen(f"{config.ASSET_PATH}health.png", confidence=config.CONFIDENCE)
                except pyautogui.ImageNotFoundException:
                    health_visible = None

                if menu_visible and health_visible:
                    print("[~] Menu and health bar detected. Pressing 'X' key to close menu.")
                    keyboard.press_and_release('x')
                    time.sleep(15)
                    break

                time.sleep(1)

    # Step 5: Walk forward to reset location
    keyboard.press('up')
    time.sleep(7)
    keyboard.release('up')

if __name__ == "__main__":
    main()
