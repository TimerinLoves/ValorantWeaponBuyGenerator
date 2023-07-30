import random
import tkinter as tk
from PIL import Image, ImageTk
import pyautogui
import pytesseract
import os
from pynput import keyboard
import time
import threading

last_purchase = None
prev_b_key_time = 0
key_press_threshold = 1
b_key_binding = 'p'  # Default Generation Keybind

def get_credits_from_screen():
    
    pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    
    # Adjust these coordinates to capture the region where the credits are displayed in Valorant.
    # You can use a screenshot tool to find the exact coordinates.
    credits_region = (1772, 1029, 143, 30)  # Replace x, y, width, and height with appropriate values.

    # Capture the screen in the specified region
    screenshot = pyautogui.screenshot(region=credits_region)

    # Perform OCR on the captured image to extract text
    credit_text = pytesseract.image_to_string(screenshot, config='--psm 6')

    # Parse the extracted text to obtain the credit value (assuming it's a number)
    credits = int(''.join(filter(str.isdigit, credit_text)))

    return credits

def suggest_purchase(credits):
    global last_purchase

    weapons = [
        (0, 'Knife'),
        (0, 'Classic'),
        (300, 'Shorty'),
        (450, 'Frenzy'),
        (500, 'Ghost'),
        (800, 'Sheriff'),
        (1100, 'Stinger'),
        (1600, 'Spectre'),
        (850, 'Bucky'),
        (1850, 'Judge'),
        (2050, 'Bulldog'),
        (950, 'Marshal'),
        (2250, 'Guardian'),
        (1600, 'Ares'),
        (4700, 'Operator'),
        (2900, 'Phantom'),
        (2900, 'Vandal'),
        (3200, 'Odin')
    ]

    armor = {
        0:   'No Armor',
        400: 'Light Armor',
        1000: 'Heavy Armor'
    }

    if credits < 0:
        return "Not enough credits to buy anything."

    possible_combinations = []

    # Generate all possible combinations
    for weapon_cost, weapon in weapons:
        for armor_cost, armor_type in armor.items():
            if weapon_cost + armor_cost <= credits:
                combination = {
                    'weapon': weapon,
                    'armor': armor_type,
                }
                if combination != last_purchase:  # Check if the combination is different from the last purchase
                    possible_combinations.append(combination)

    if not possible_combinations:
        return "Cannot buy anything with the available credits."

    # Randomly select one combination from possible_combinations
    random_combination = random.choice(possible_combinations)
    last_purchase = random_combination  # Update the last purchase with the new selection
    return random_combination

def get_script_directory():
    return os.path.dirname(os.path.abspath(__file__))

def get_weapon_image_path(weapon_name):
    script_dir = get_script_directory()
    return os.path.join(script_dir, 'weapons', weapon_name.lower() + '.gif')

def get_armor_image_path(armor_name):
    script_dir = get_script_directory()
    return os.path.join(script_dir, 'armor', armor_name.lower() + '.gif')

def get_suggested_purchase():
    global prev_b_key_time

    try:
        # Get credits from the screen using OCR
        user_credits = get_credits_from_screen()

        # Display the detected credits
        credits_label.config(text=f"Detected credits: {user_credits}")

        suggested_purchase = suggest_purchase(user_credits)

        print("Suggested weapon:", suggested_purchase['weapon'])  # Add this line for debugging

        # Load weapon image
        weapon_img_path = get_weapon_image_path(suggested_purchase['weapon'])
        print("Weapon image path:", weapon_img_path)

        if os.path.exists(weapon_img_path):
            weapon_img = Image.open(weapon_img_path)
            weapon_img = weapon_img.resize((100, 100))
            weapon_img = ImageTk.PhotoImage(weapon_img)
            weapon_label.config(image=weapon_img, text=suggested_purchase['weapon'], compound=tk.TOP)
            weapon_label.image = weapon_img
        else:
            weapon_label.config(text="Image not found for " + suggested_purchase['weapon'])
            weapon_label.image = None

        # Load armor image
        armor_img_path = get_armor_image_path(suggested_purchase['armor'])
        armor_img = Image.open(armor_img_path)
        armor_img = armor_img.resize((100, 100))
        armor_img = ImageTk.PhotoImage(armor_img)
        armor_label.config(image=armor_img, text=suggested_purchase['armor'], compound=tk.TOP)
        armor_label.image = armor_img
        
    except ValueError:
        weapon_label.config(text="Invalid input or unable to read credits from the screen.")
        armor_label.config(text="")
        return

def on_key_press(key):
    global b_key_binding

    try:
        if key.char == b_key_binding:
            on_b_key_press()
    except AttributeError:
        pass

def on_b_key_press():
    global prev_b_key_time

    current_time = time.time()
    if current_time - prev_b_key_time >= key_press_threshold:
        get_suggested_purchase()
        prev_b_key_time = current_time

    print(f"{b_key_binding.upper()} key pressed.")
    print("Suggested weapon:", weapon_label.cget("text"))

def pynput_listener():
    with keyboard.Listener(on_press=on_key_press) as listener:
        listener.join()

def update_key_binding():
    global b_key_binding
    new_binding = key_binding_entry.get()
    if new_binding:
        b_key_binding = new_binding.lower()
    key_binding_entry.delete(0, tk.END)

# Create the Tkinter window
root = tk.Tk()

# Remove window decorations (title bar, borders, etc.)
root.overrideredirect(1)

# Set window transparency and always on top
root.attributes("-alpha", 0.7)  # Set the alpha value between 0 (fully transparent) and 1 (opaque)
root.attributes("-topmost", True)

# Custom title bar frame
title_bar = tk.Frame(root, bg="#333333", relief=tk.SUNKEN, bd=0)
title_bar.pack(fill=tk.X, padx=0, pady=0, ipadx=0, ipady=0, anchor="n")

# Close button on the title bar
def close_window():
    root.destroy()

close_button = tk.Button(title_bar, text="X", bg="#333333", fg="white", command=close_window)
close_button.pack(side=tk.RIGHT, padx=5)

# Set fixed window size
window_width, window_height = 360, 200
root.geometry(f"{window_width}x{window_height}")

# Make the window draggable
def on_drag(event):
    x = root.winfo_pointerx() - root._offset_x
    y = root.winfo_pointery() - root._offset_y
    root.geometry("+%d+%d" % (x, y))

def on_drag_start(event):
    root._offset_x = event.x
    root._offset_y = event.y

title_bar.bind("<B1-Motion>", on_drag)
title_bar.bind("<ButtonPress-1>", on_drag_start)

# Create widgets
credits_label = tk.Label(root, text="Detected credits: N/A")  # Initial value before scanning
credits_entry = tk.Entry(root)
weapon_label = tk.Label(root)
armor_label = tk.Label(root)
key_binding_label = tk.Label(root, text="Rebind Generating key to (Default P):")
key_binding_entry = tk.Entry(root)

# Grid layout with adjustments
title_bar.grid(row=0, column=0, columnspan=2, sticky="ew")
credits_label.grid(row=1, column=0, padx=10, pady=5, columnspan=2)
weapon_label.grid(row=2, column=0, padx=10, pady=5)
armor_label.grid(row=2, column=1, padx=10, pady=5)
key_binding_label.grid(row=3, column=0, padx=10, pady=5)
key_binding_entry.grid(row=3, column=1, padx=10, pady=5)

# Create the listener for user-specified key press event
key_binding_button = tk.Button(root, text="Update Binding", command=update_key_binding)
key_binding_button.grid(row=4, columnspan=2, padx=10, pady=5)

# Create the listener for 'B' key press event
keyboard_listener = keyboard.Listener(on_press=on_key_press)
keyboard_listener.start()

# Start the pynput keypress listener in a separate thread
listener_thread = threading.Thread(target=pynput_listener, daemon=True)
listener_thread.start()

# Run the Tkinter event loop
root.mainloop()
