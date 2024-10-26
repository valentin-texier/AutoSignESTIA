import os
import json
import threading
import shutil
import tkinter as tk
from dataclasses import dataclass
import time
from tkinter import messagebox
from typing import Optional, List, Tuple
import pyperclip
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@dataclass
class AppConfig:
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CHROME_DRIVER_PATH: str = os.path.join(BASE_DIR, 'ressources', 'chromedriver.exe')
    CONFIG_PATH: str = os.path.join(BASE_DIR, 'config', 'config.json')
    DOWNLOAD_DIR: str = os.path.join(BASE_DIR, 'automation')
    ICON_PATH: str = os.path.join(BASE_DIR, "ressources", "favicon.ico")


class BaseWindow:
    def __init__(self, master, title: str, resizable: bool = False):
        self.master = master
        self.master.title(title)
        self.master.configure(bg="white")
        self.master.resizable(False, False) if not resizable else None
        self.set_window_icon()
        self.center_window()

    def set_window_icon(self):
        self.master.iconbitmap(AppConfig.ICON_PATH)

    def center_window(self, width: int = 400, height: int = 300):
        x_coordinate = (self.master.winfo_screenwidth() - width) // 2
        y_coordinate = (self.master.winfo_screenheight() - height) // 2
        self.master.geometry(f"{width}x{height}+{x_coordinate}+{y_coordinate}")

    def create_button(self, frame, text: str, command, button_type: str = "primary") -> tk.Button:
        styles = {
            "primary": {"bg": "#2196F3", "hover": "#1976D2", "fg": "white"},
            "secondary": {"bg": "white", "hover": "#e0e0e0", "fg": "#2196F3"}
        }
        style = styles[button_type]

        button = tk.Button(
            frame,
            text=text,
            command=command,
            bg=style["bg"],
            fg=style["fg"],
            relief="flat",
            borderwidth=0,
            font=("Helvetica", 10),
            width=10
        )
        button.bind("<Enter>", lambda e: button.config(bg=style["hover"]))
        button.bind("<Leave>", lambda e: button.config(bg=style["bg"]))
        return button


class ConfigManager:
    @staticmethod
    def load_config() -> dict:
        try:
            with open(AppConfig.CONFIG_PATH, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            messagebox.showwarning("Avertissement", "Le fichier de configuration n'existe pas.")
            return {}

    @staticmethod
    def save_config(config: dict):
        os.makedirs(os.path.dirname(AppConfig.CONFIG_PATH), exist_ok=True)
        with open(AppConfig.CONFIG_PATH, 'w') as file:
            json.dump(config, file, indent=4)


class ConfigIdentifiant(BaseWindow):
    def __init__(self, master):
        super().__init__(master, "Configuration des Identifiants")
        self.create_widgets()
        self.load_config()

    def create_widgets(self):
        frame = tk.Frame(self.master, bg="white")
        frame.pack(expand=True)

        tk.Label(frame, text="Veuillez entrer votre info pour vous connecter à Pegasus :", bg="white", font=("Helvetica", 10)).pack(pady=(10, 5))
        self.email_entry = self.create_entry_field(frame, "Email de l'ESTIA :")
        self.password_entry = self.create_entry_field(frame, "Mot de Passe :", show="*")

        self.show_password_var = tk.BooleanVar()
        tk.Checkbutton(frame, text="Afficher le mot de passe", variable=self.show_password_var, command=self.toggle_password_visibility, bg="white").pack(anchor="w", padx=20)
        self.create_button_frame()

    def create_button_frame(self):
        button_frame = tk.Frame(self.master, bg="white")
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 10))
        self.create_button(button_frame, "Suivant", self.save_credentials, "primary").grid(row=0, column=1, padx=(140, 40), pady=(0, 10), sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

    def create_entry_field(self, frame, label: str, show: Optional[str] = None) -> tk.Entry:
        tk.Label(frame, text=label, bg="white", font=("Helvetica", 10)).pack(anchor="w", padx=(20, 0), pady=(10, 0))
        entry = tk.Entry(frame, width=40, show=show)
        entry.pack(anchor="w", padx=(20, 0), pady=(0, 5))
        return entry

    def load_config(self):
        config = ConfigManager.load_config()
        self.email_entry.insert(0, config.get("username", ""))
        self.password_entry.insert(0, config.get("password", ""))

    def toggle_password_visibility(self):
        self.password_entry.config(show="" if self.show_password_var.get() else "*")

    def save_credentials(self):
        config = ConfigManager.load_config()
        config.update({
            "username": self.email_entry.get() or config.get("username", ""),
            "password": self.password_entry.get() or config.get("password", "")
        })
        ConfigManager.save_config(config)
        self.master.destroy()
        self.open_next_window()

    def open_next_window(self):
        root = tk.Tk()
        CalendarConfig(root)
        root.mainloop()


class WebDriverManager:
    @staticmethod
    def create_driver() -> webdriver.Chrome:
        options = Options()
        prefs = {
            "download.default_directory": AppConfig.BASE_DIR,
            "download.prompt_for_download": False,
            "directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')

        service = Service(AppConfig.CHROME_DRIVER_PATH)
        return webdriver.Chrome(service=service, options=options)


class CalendarConfig(BaseWindow):
    def __init__(self, master):
        super().__init__(master, "Télécharger son calendrier")
        self.create_widgets()

    def create_widgets(self):
        label_frame = tk.Frame(self.master, bg="white")
        label_frame.pack(expand=True, pady=(10, 5))

        tk.Label(label_frame, text="Télécharger son calendrier de l'ESTIA sur PEGASUS :", bg="white", font=("Helvetica", 10)).pack(expand=True, pady=(60, 0))
        center_frame = tk.Frame(self.master, bg="white")
        center_frame.pack(expand=True, pady=(0, 40))

        download_button = self.create_button(center_frame, "Télécharger", self.download_calendar, "primary")
        download_button.config(width=20)
        download_button.pack(pady=20)
        self.create_button_frame()

    def create_button_frame(self):
        button_frame = tk.Frame(self.master, bg="white")
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 10))
        self.create_button(button_frame, "Suivant", self.open_next_window, "primary").grid(row=0, column=1, padx=(140, 40), pady=(0, 10), sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

    def download_calendar(self):
        threading.Thread(target=self.start_download).start()

    def start_download(self):
        try:
            config = ConfigManager.load_config()
            driver = WebDriverManager.create_driver()
            self.perform_download(driver, config)
            driver.quit()
            self.move_calendar_file()
            messagebox.showinfo("Succès", "Le téléchargement a été effectué avec succès.")
        except Exception as e:
            print(f"Erreur lors du téléchargement: {e}")
            messagebox.showerror("Erreur", f"Erreur lors du téléchargement.")

    def perform_download(self, driver: webdriver.Chrome, config: dict):
        driver.get('https://learning.estia.fr/pegasus/index.php')
        wait = WebDriverWait(driver, 1)

        wait.until(EC.visibility_of_element_located((By.ID, "inputLogin"))).send_keys(config["username"])
        wait.until(EC.visibility_of_element_located((By.ID, "inputPassword"))).send_keys(config["password"])
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))).click()

        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.km-menus-group:nth-child(2) .title-text'))).click()
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#menu_item_1 a:nth-child(3) .menu-item'))).click()

        iframe = wait.until(EC.visibility_of_element_located((By.TAG_NAME, "iframe")))
        driver.switch_to.frame(iframe)

        download_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button > .texte')))
        download_button.click()

        download_link = pyperclip.paste()
        if download_link:
            driver.get(download_link)
        else:
            messagebox.showwarning("Avertissement", "Le lien de téléchargement n'a pas été trouvé dans le presse-papiers.")
            raise ValueError("Le lien de téléchargement n'a pas été trouvé dans le presse-papiers.")

        WebDriverWait(driver, 5).until(
            lambda d: os.path.exists(os.path.join(AppConfig.BASE_DIR, 'calendar.ics'))
        )

    def move_calendar_file(self):
        source = os.path.join(AppConfig.BASE_DIR, 'calendar.ics')
        destination = os.path.join(AppConfig.DOWNLOAD_DIR, 'calendar.ics')
        os.makedirs(AppConfig.DOWNLOAD_DIR, exist_ok=True)
        if os.path.exists(destination):
            os.remove(destination)
        shutil.move(source, destination)

    def open_next_window(self):
        self.master.destroy()
        root = tk.Tk()
        ExecutionConfig(root)
        root.mainloop()


class ExecutionConfig(BaseWindow):
    def __init__(self, master):
        super().__init__(master, "Configuration d'Exécution")
        self.create_widgets()
        self.create_button_frame()

    def create_widgets(self):
        frame = tk.Frame(self.master, bg="white")
        frame.pack(expand=True)

        self.execution_mode_var = tk.StringVar(value="manual")
        self.create_section(
            frame,
            "Choisissez votre mode d'exécution pour l'auto émargement :",
            [("Manuel", "manual"), ("Automatique", "automatic")],
            self.execution_mode_var
        )

        self.headless_mode_var = tk.StringVar(value="oui")
        self.create_section(
            frame,
            "Voir le script en direct effectuer les tâches :",
            [("Oui", "non"), ("Non", "oui")],
            self.headless_mode_var
        )

    def create_section(self, parent, label_text: str, options: List[Tuple[str, str]], variable: tk.StringVar):
        tk.Label(parent, text=label_text, bg="white", font=("Helvetica", 10)).pack(anchor="w", padx=20, pady=(20, 10))
        for text, value in options:
            tk.Radiobutton(parent, text=text, variable=variable, value=value, bg="white").pack(anchor="w", padx=40)

    def create_button_frame(self):
        button_frame = tk.Frame(self.master, bg="white")
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 10))
        self.create_button(button_frame, "Suivant", self.save_execution_config, "primary").grid(row=0, column=1, padx=(140, 40), pady=(0, 10), sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

    def save_execution_config(self):
        try:
            config = ConfigManager.load_config()
            config.update({
                'execution_mode': self.execution_mode_var.get(),
                'headless_mode': self.headless_mode_var.get()
            })
            ConfigManager.save_config(config)
            self.master.destroy()
            self.open_signature_creator()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement de la configuration.")

    def open_signature_creator(self):
        root = tk.Tk()
        SignatureCreatorUI(root)
        root.mainloop()


class SignatureCreator:
    SIGNATURE_FILE = 'signatures.txt'
    ANIMATION_DELAY = 0.005

    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.reset_state()
        self.load_signatures()

    def reset_state(self):
        self.is_drawing = False
        self.current_signature = 0
        self.signatures: List[List[Tuple[int, int]]] = []
        self.points: List[Tuple[int, int]] = []
        self.drawing_thread: Optional[threading.Thread] = None
        self.drawing_in_progress = False

    def load_signatures(self):
        try:
            with open(self.SIGNATURE_FILE, 'r') as file:
                self.signatures = [self.parse_coordinates(line) for line in file]
        except FileNotFoundError:
            messagebox.showwarning("Avertissement", f"Le fichier '{self.SIGNATURE_FILE}' n'existe pas.")
        except Exception as e:
            messagebox.showerror("Erreur", "Erreur lors du chargement des signatures.")

    @staticmethod
    def parse_coordinates(line: str) -> List[Tuple[int, int]]:
        try:
            coordinates = list(map(int, line.strip().split()))
            if len(coordinates) % 2 != 0:
                raise ValueError("Les coordonnées doivent être en paires.")
            return [(coordinates[i], coordinates[i + 1]) for i in range(0, len(coordinates), 2)]
        except Exception as e:
            messagebox.showerror("Erreur", "Erreur lors de l'analyse des coordonnées.")
            return []

    def handle_drawing_events(self, event_type: str, event):
        handlers = {
            "start": self.start_drawing,
            "draw": self.draw_signature,
            "stop": self.stop_drawing
        }
        handler = handlers.get(event_type)
        if handler:
            handler(event)

    def start_drawing(self, event):
        self.is_drawing = True
        self.clear_canvas()
        self.stop_drawing_signature()
        self.points = [(event.x, event.y)]

    def draw_signature(self, event):
        if not self.is_drawing:
            return
        x, y = event.x, event.y
        self.points.append((x, y))
        if len(self.points) > 1:
            prev_x, prev_y = self.points[-2]
            self.canvas.create_line(prev_x, prev_y, x, y, fill="black", width=2)

    def stop_drawing(self, event):
        if not self.is_drawing:
            return
        self.is_drawing = False
        self.points.append((event.x, event.y))
        self.save_signature()

    def save_signature(self):
        try:
            with open(self.SIGNATURE_FILE, 'a') as file:
                coordinates = ' '.join(f"{x} {y}" for x, y in self.points)
                file.write(f"{coordinates}\n")
        except Exception as e:
            messagebox.showerror("Erreur", "Erreur lors de la sauvegarde de la signature.")

    def clear_canvas(self):
        self.canvas.delete("all")

    def load_and_draw_signature(self):
        if not self.signatures:
            messagebox.showwarning("Avertissement", "Aucune signature disponible.")
            return

        self.current_signature %= len(self.signatures)
        self.clear_canvas()
        self.drawing_in_progress = True
        self.drawing_thread = threading.Thread(target=self.animate_signature)
        self.drawing_thread.daemon = True
        self.drawing_thread.start()

    def animate_signature(self):
        try:
            signature = self.signatures[self.current_signature]
            for i in range(len(signature) - 1):
                if not self.drawing_in_progress:
                    break

                x1, y1 = signature[i]
                x2, y2 = signature[i + 1]

                self.canvas.after(0, lambda: self.canvas.create_line(x1, y1, x2, y2, fill="black", width=2))
                time.sleep(self.ANIMATION_DELAY)

            self.current_signature += 1
        except Exception as e:
            print(f"Erreur lors de l'animation : {e}")
            self.stop_drawing_signature()

    def stop_drawing_signature(self):
        self.drawing_in_progress = False
        self.clear_canvas()


class SignatureCreatorUI(BaseWindow):
    def __init__(self, master):
        super().__init__(master, "Créateur de Signature")
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.master, text="Dessinez votre signature :", anchor="center", bg="white", font=("Helvetica", 10)).pack(pady=(10, 5))
        self.create_drawing_canvas()
        self.create_button_frame()

    def create_drawing_canvas(self):
        canvas = tk.Canvas(self.master, bg="white", width=170, height=170)
        canvas.pack(pady=(5, 10))

        self.signature_creator = SignatureCreator(canvas)

        canvas.bind("<Button-1>", lambda e: self.signature_creator.handle_drawing_events("start", e))
        canvas.bind("<B1-Motion>", lambda e: self.signature_creator.handle_drawing_events("draw", e))
        canvas.bind("<ButtonRelease-1>", lambda e: self.signature_creator.handle_drawing_events("stop", e))

    def create_button_frame(self):
        button_frame = tk.Frame(self.master, bg="white")
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 10))

        self.create_button(button_frame, "Charger Signature", self.signature_creator.load_and_draw_signature, "secondary").grid(row=0, column=0, padx=(30, 10), pady=(0, 10), sticky="ew")
        self.create_button(button_frame, "Quitter", self.master.destroy, "primary").grid(row=0, column=1, padx=(10, 30), pady=(0, 10), sticky="ew")

        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)


if __name__ == "__main__":
    root = tk.Tk()
    ConfigIdentifiant(root)
    root.mainloop()