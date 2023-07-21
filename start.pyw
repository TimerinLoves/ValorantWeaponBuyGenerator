import random
import tkinter as tk
from PIL import Image, ImageTk
import pyautogui
import pytesseract
import os
from pynput import keyboard
import time

last_purchase = None
prev_b_key_time = 0
key_press_threshold = 1
b_key_binding = 'p'  # Default Generation Keybind

def get_credits_from_screen():
    
    pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    
    # Adjust these coordinates to capture the region where the credits are displayed in Valorant.
    # You can use a screenshot tool to find the exact coordinates.
    credits_region = (1813, 1037, 57, 15)  # Replace x, y, width, and height with appropriate values.

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
        weapon_img_path = 'weapons/' + suggested_purchase['weapon'].lower() + '.gif'
        print("Weapon image path:", weapon_img_path)  # Add this line for debugging

        weapon_img = Image.open(weapon_img_path)
        weapon_img = weapon_img.resize((100, 100))  # Resize the image if needed
        weapon_img = ImageTk.PhotoImage(weapon_img)
        weapon_label.config(image=weapon_img, text=suggested_purchase['weapon'], compound=tk.TOP)
        weapon_label.image = weapon_img  # Keep a reference to prevent garbage collection

        # Load armor image
        armor_img_path = 'armor/' + suggested_purchase['armor'].lower() + '.gif'
        armor_img = Image.open(armor_img_path)
        armor_img = armor_img.resize((100, 100))  # Resize the image if needed
        armor_img = ImageTk.PhotoImage(armor_img)
        armor_label.config(image=armor_img, text=suggested_purchase['armor'], compound=tk.TOP)
        armor_label.image = armor_img  # Keep a reference to prevent garbage collection

    except ValueError:
        weapon_label.config(text="Invalid input or unable to read credits from the screen.")
        armor_label.config(text="")
        return

def on_b_key_press():
    global prev_b_key_time

    current_time = time.time()
    if current_time - prev_b_key_time >= key_press_threshold:
        get_suggested_purchase()
        prev_b_key_time = current_time

    print(f"{b_key_binding.upper()} key pressed.")
    print("Suggested weapon:", weapon_label.cget("text"))

def on_key_press(key):
    global b_key_binding

    try:
        if key.char == b_key_binding:
            on_b_key_press()
    except AttributeError:
        pass

def update_key_binding():
    global b_key_binding
    new_binding = key_binding_entry.get()
    if new_binding:
        b_key_binding = new_binding.lower()
    key_binding_entry.delete(0, tk.END)

# Create a Tkinter window
root = tk.Tk()
root.title("Valorant Suggested Purchase")

# Create widgets
credits_label = tk.Label(root, text="Detected credits: N/A")  # Initial value before scanning
credits_entry = tk.Entry(root)
suggest_button = tk.Button(root, text="Get Suggested Purchase", command=get_suggested_purchase)
weapon_label = tk.Label(root)
armor_label = tk.Label(root)
key_binding_label = tk.Label(root, text="Rebind Generating key to (Default P):")
key_binding_entry = tk.Entry(root)

# Grid layout
credits_label.grid(row=0, column=0, padx=10, pady=5)
credits_entry.grid(row=0, column=1, padx=10, pady=5)
suggest_button.grid(row=1, columnspan=2, padx=10, pady=5)
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

# Run the Tkinter event loop
root.mainloop()
