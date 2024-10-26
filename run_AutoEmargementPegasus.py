import math
import random
import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import json
import os
import requests

base_dir = os.path.dirname(os.path.abspath(__file__))
chromedriver_path = os.path.join(base_dir, 'ressources', 'chromedriver.exe')
config_path = os.path.join(base_dir, 'config', 'config.json')


def load_config():
    try:
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
            return config.get('username'), config.get('password'), config.get('headless_mode', False), config.get(
                'execution_mode', 'manual')
    except FileNotFoundError:
        messagebox.showerror("Erreur de configuration", f"Le fichier '{config_path}' n'existe pas.")
        raise


def wait_for_element(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((by, value)))


def load_signatures(file_path):
    signatures = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                coordinates = list(map(int, line.strip().split()))
                signatures.append([tuple(coordinates[i:i + 2]) for i in range(0, len(coordinates), 2)])
    except FileNotFoundError:
        messagebox.showerror("Fichier manquant",
                             f"Le fichier '{file_path}' n'existe pas. Veuillez vérifier le dossier de configuration.")
    except ValueError as e:
        messagebox.showerror("Erreur de format", f"Erreur lors du chargement des coordonnées")
    return signatures


def draw_signature(driver, canvas, signature_points, offset_x=-100, offset_y=-80):
    actions = ActionChains(driver)
    start_x, start_y = signature_points[0][0] + offset_x, signature_points[0][1] + offset_y
    actions.move_to_element_with_offset(canvas, start_x, start_y).click_and_hold()
    for point in signature_points[1:]:
        adjusted_x, adjusted_y = point[0] + offset_x, point[1] + offset_y
        actions.move_by_offset(adjusted_x - start_x, adjusted_y - start_y)
        start_x, start_y = adjusted_x, adjusted_y
    actions.release().perform()


def check_location():
    messages = [
        "Oups, tu n’es pas là… essaie d’arriver avant qu’il soit trop tard !",
        "Localisation incorrecte. Cours vite avant qu’ils ne s’en rendent compte !",
        "Allez, accélère ! Tu dois être sur place pour émarger.",
        "Houston, on a un problème… tu n’es pas à l’ESTIA !",
        "Où te caches-tu ? Rejoins-nous à l’ESTIA pour émarger !",
        "C’est interdit d’émarger depuis ici… reprends la route vers l’ESTIA !",
        "Erreur : il semble que tu sois à des kilomètres de l’ESTIA.",
        "Essaye encore, mais à l’ESTIA cette fois !",
        "La magie ne fonctionne pas à distance, désolé !",
        "Impossible d'émarger ici, direction l'ESTIA !"
    ]

    try:
        response = requests.get("http://ip-api.com/json/")
        location_data = response.json()
        if location_data['status'] == 'success':
            workplace_lat, workplace_lon = 43.437611, -1.558704
            current_lat, current_lon = location_data['lat'], location_data['lon']
            distance = 6371 * 2 * math.asin(math.sqrt(
                math.sin(math.radians(current_lat - workplace_lat) / 2) ** 2 +
                math.cos(math.radians(workplace_lat)) * math.cos(math.radians(current_lat)) *
                math.sin(math.radians(current_lon - workplace_lon) / 2) ** 2))
            if distance > 1.0:
                messagebox.showwarning("Émargement impossible", random.choice(messages))
                return False
            return True
        else:
            messagebox.showerror("Erreur de localisation",
                                 f"Erreur lors de la localisation : {location_data.get('message', 'Inconnu')}")
            return False
    except requests.RequestException as e:
        messagebox.showerror("Erreur de connexion", f"Erreur de requête pour obtenir la localisation.")
        return False


def run_emargement_script():
    username, password, headless_mode, execution_mode = load_config()

    options = Options()
    if headless_mode == "oui":
        options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get('https://learning.estia.fr/pegasus/index.php')
        wait_for_element(driver, By.ID, "inputLogin").send_keys(username)
        wait_for_element(driver, By.ID, "inputPassword").send_keys(password)
        wait_for_element(driver, By.CSS_SELECTOR, "input[type='submit']").click()

        wait_for_element(driver, By.CSS_SELECTOR, '.km-menus-group:nth-child(2) .title-text').click()
        wait_for_element(driver, By.CSS_SELECTOR, '#menu_item_1 a:nth-child(2) .menu-item').click()

        iframe = wait_for_element(driver, By.TAG_NAME, "iframe")
        driver.switch_to.frame(iframe)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.wc-cal-event')))
        events = driver.find_elements(By.CSS_SELECTOR, '.wc-cal-event')

        target_color = 'rgba(245, 161, 62, 1)'
        selected_event = next(
            (event for event in events if event.value_of_css_property('background-color') == target_color), None)
        if selected_event:
            selected_event.click()
            canvas = wait_for_element(driver, By.CSS_SELECTOR, '#cboxLoadedContent canvas')
            signatures = load_signatures(os.path.join(base_dir, 'config', 'signatures.txt'))
            if signatures:
                draw_signature(driver, canvas, random.choice(signatures))
            else:
                messagebox.showinfo("Aucune signature disponible",
                                    "Le fichier de signatures est vide. Ajoutez des signatures depuis 'setup_config' pour continuer.")
                return

            wait_for_element(driver, By.CSS_SELECTOR, '#cboxLoadedContent .button-action').click()
            wait_for_element(driver, By.CSS_SELECTOR, '.swal2-confirm').click()
        else:
            messagebox.showinfo("Aucun événement", "Aucun événement trouvé pour émarger.")

    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur rencontrée : {e}")
    finally:
        driver.quit()


def create_interface():
    root = tk.Tk()
    root.title("Émargement ?")
    root.configure(bg="white")
    root.resizable(False, False)
    screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()
    x_coordinate, y_coordinate = (screen_width // 2) - (300 // 2), (screen_height // 2) - (150 // 2)
    root.geometry(f"300x150+{x_coordinate}+{y_coordinate}")

    message = tk.Label(root, text="Voulez-vous émarger maintenant ?", anchor="center", bg="white",
                       font=("Helvetica", 10))
    message.pack(expand=True)

    button_frame = tk.Frame(root, bg="white")
    button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 10))

    btn_oui = tk.Button(button_frame, text="Oui", command=lambda: (root.destroy(), run_emargement_script()),
                        bg="#2196F3", fg="white", relief="flat", borderwidth=0, font=("Helvetica", 10), width=10)
    btn_oui.grid(row=0, column=0, padx=(30, 10), pady=(0, 10), sticky="ew")
    btn_oui.bind("<Enter>", lambda event: btn_oui.config(bg='#1976D2', fg='white'))
    btn_oui.bind("<Leave>", lambda event: btn_oui.config(bg='#2196F3', fg='white'))

    btn_non = tk.Button(button_frame, text="Non", command=root.destroy, bg="white", fg="#2196F3", relief="flat",
                        borderwidth=0, font=("Helvetica", 10), width=10)
    btn_non.grid(row=0, column=1, padx=(10, 30), pady=(0, 10), sticky="ew")
    btn_non.bind("<Enter>", lambda event: btn_non.config(bg='#e0e0e0', fg='#2196F3'))
    btn_non.bind("<Leave>", lambda event: btn_non.config(bg='white', fg='#2196F3'))

    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)

    icon_path = os.path.join(base_dir, "ressources", "favicon.ico")
    root.iconbitmap(icon_path)

    root.mainloop()


if __name__ == "__main__":
    username, password, headless_mode, execution_mode = load_config()
    if execution_mode == "manual":
        create_interface()
    else:
        run_emargement_script()
