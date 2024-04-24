import datetime
import os

import pandas as pd
from pynput import keyboard

current_keys = set()

df = pd.DataFrame(columns=["Keyboard Shortcut", "Time"])

df = pd.read_csv(
    "/Users/haseab/Desktop/Desktop/backed-up/backed-scripts/Python/TiBA/src/keyboard_shortcut_launches.csv"
)


def on_press(key):
    global current_keys, df
    try:
        # print(current_keys)
        # print(key)
        if keyboard.Key.cmd not in current_keys and key == keyboard.Key.cmd:
            current_keys.add(key)
            # print("cmd added to current_keys")
        if keyboard.Key.ctrl not in current_keys and key == keyboard.Key.ctrl:
            current_keys.add(key)
            # print("ctrl added to current_keys")
        if keyboard.Key.shift not in current_keys and key == keyboard.Key.shift:
            current_keys.add(key)
            # print("shift added to current_keys")
        if keyboard.Key.alt not in current_keys and key == keyboard.Key.alt:
            current_keys.add(key)
            # print("alt added to current_keys")

        if key not in [
            keyboard.Key.alt,
            keyboard.Key.cmd,
            keyboard.Key.ctrl,
            keyboard.Key.shift,
        ]:
            current_keys.add(key)
            # Check for Command + `
            if (
                keyboard.Key.cmd in current_keys
                and keyboard.KeyCode.from_char("`") in current_keys
            ):
                print(
                    f"Command + ` Keyboard Shortcut Pressed at {datetime.datetime.now()}"
                )
                df = pd.concat(
                    [
                        df,
                        pd.DataFrame(
                            [[f"Command + `", datetime.datetime.now()]],
                            columns=["Keyboard Shortcut", "Time"],
                        ),
                    ]
                )

            # Check for Command + 1-9
            if hasattr(key, "char") and key.char is not None and key.char.isdigit():
                if keyboard.Key.cmd in current_keys and 0 <= int(key.char) <= 9:
                    print(
                        f"Command + {key.char} Keyboard Shortcut Pressed at {datetime.datetime.now()}"
                    )
                    df = pd.concat(
                        [
                            df,
                            pd.DataFrame(
                                [[f"Command + {key.char}", datetime.datetime.now()]],
                                columns=["Keyboard Shortcut", "Time"],
                            ),
                        ]
                    )

            # Check for Ctrl + Shift + O (^ + Shift + O)
            if (
                keyboard.Key.ctrl in current_keys
                and keyboard.Key.shift in current_keys
                and keyboard.KeyCode.from_char("c") in current_keys
            ):
                print(
                    f"Ctrl + Shift + C Keyboard Shortcut Pressed at {datetime.datetime.now()}"
                )
                df = pd.concat(
                    [
                        df,
                        pd.DataFrame(
                            [[f"Ctrl + Shift + C", datetime.datetime.now()]],
                            columns=["Keyboard Shortcut", "Time"],
                        ),
                    ]
                )

            # Check for Ctrl + Shift + E (^ + Shift + E)
            if (
                keyboard.Key.ctrl in current_keys
                and keyboard.Key.shift in current_keys
                and keyboard.KeyCode.from_char("e") in current_keys
            ):
                print(
                    f"Ctrl + Shift + W Keyboard Shortcut Pressed at {datetime.datetime.now()}"
                )
                df = pd.concat(
                    [
                        df,
                        pd.DataFrame(
                            [[f"Ctrl + Shift + W", datetime.datetime.now()]],
                            columns=["Keyboard Shortcut", "Time"],
                        ),
                    ]
                )

            # Check for Command + Shift + C
            if (
                keyboard.Key.cmd in current_keys
                and keyboard.Key.shift in current_keys
                and keyboard.KeyCode.from_char("c") in current_keys
            ):
                print(
                    f"Command + Shift + C Keyboard Shortcut Pressed at {datetime.datetime.now()}"
                )
                df = pd.concat(
                    [
                        df,
                        pd.DataFrame(
                            [[f"Command + Shift + C", datetime.datetime.now()]],
                            columns=["Keyboard Shortcut", "Time"],
                        ),
                    ]
                )

            # Check for Command + Shift + Space
            if (
                keyboard.Key.cmd in current_keys
                and keyboard.Key.shift in current_keys
                and keyboard.Key.space in current_keys
            ):
                print(
                    f"Command + Shift + Space Keyboard Shortcut Pressed at {datetime.datetime.now()}"
                )
                df = pd.concat(
                    [
                        df,
                        pd.DataFrame(
                            [[f"Command + Shift + Space", datetime.datetime.now()]],
                            columns=["Keyboard Shortcut", "Time"],
                        ),
                    ]
                )

            # Check for Command + Space
            if (
                keyboard.Key.cmd in current_keys
                and keyboard.Key.space in current_keys
                and len(current_keys) == 2
            ):
                print(
                    f"Command + Space Keyboard Shortcut Pressed at {datetime.datetime.now()}"
                )
                df = pd.concat(
                    [
                        df,
                        pd.DataFrame(
                            [[f"Command + Space", datetime.datetime.now()]],
                            columns=["Keyboard Shortcut", "Time"],
                        ),
                    ]
                )

            # Check for Ctrl + Shift + O (^ + Shift + O)
            if (
                keyboard.Key.ctrl in current_keys
                and keyboard.Key.shift in current_keys
                and keyboard.KeyCode.from_char("o") in current_keys
            ):
                print(
                    f"Ctrl + Shift + O Keyboard Shortcut Pressed at {datetime.datetime.now()}"
                )
                df = pd.concat(
                    [
                        df,
                        pd.DataFrame(
                            [[f"Ctrl + Shift + O", datetime.datetime.now()]],
                            columns=["Keyboard Shortcut", "Time"],
                        ),
                    ]
                )

            # Check for Command up, down, left, right
            if keyboard.Key.cmd in current_keys:
                for key in [
                    keyboard.Key.up,
                    keyboard.Key.down,
                    keyboard.Key.left,
                    keyboard.Key.right,
                ]:
                    if key in current_keys:
                        print(
                            f"Command + {key} Keyboard Shortcut Pressed at {datetime.datetime.now()}"
                        )
                        df = pd.concat(
                            [
                                df,
                                pd.DataFrame(
                                    [[f"Command + {key}", datetime.datetime.now()]],
                                    columns=["Keyboard Shortcut", "Time"],
                                ),
                            ]
                        )
                        break  # Exit the loop once a match is found

        df.to_csv(
            "/Users/haseab/Desktop/Desktop/backed-up/backed-scripts/Python/TiBA/src/keyboard_shortcut_launches.csv",
            index=False,
        )
    except Exception as e:
        os.system(
            f"""osascript -e 'display notification "{str(e)}" with title "Script Error" sound name "Submarine"' """
        )
        print(f"Error: {e}")


def on_release(key):
    global current_keys
    try:
        if key in current_keys:
            current_keys.remove(key)
    except Exception as e:
        os.system(
            f"""osascript -e 'display notification "{str(e)}" with title "Script Error" sound name "Submarine"' """
        )
        print(f"Error: {e}")


# Collect events until released
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
