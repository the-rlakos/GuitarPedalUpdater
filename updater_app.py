# === Simple Guitar Pedal Updater  ===

import os
import requests
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import simpledialog

# Optional background image support
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

# ----------------------------
# Settings (change here)
# ----------------------------
FIRMWARE_URL = "http://localhost:8000/firmware"
EFFECTS_URL  = "http://localhost:8000/effects"
DEFAULT_SAVE_EXT = ".bin"
CHUNK_SIZE = 1024 * 64  # 64KB chunks

class UpdaterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Guitar Pedal Updater")
        self.root.geometry("420x500")

        # Background (optional)
        if PIL_AVAILABLE and os.path.exists("tones_background.png"):
            try:
                bg_img = Image.open("tones_background.png").resize((800, 800))
                self.background_photo = ImageTk.PhotoImage(bg_img)
                bg_label = tk.Label(root, image=self.background_photo)
                bg_label.place(relwidth=1, relheight=1)
            except Exception:
                pass

        # Main container
        wrapper = tk.Frame(root, bg="#ffffff", bd=0, highlightthickness=0)
        wrapper.pack(fill="both", expand=True, padx=12, pady=12)

        title_label = tk.Label(
            wrapper, text="Guitar Pedal Updater",
            font=("Helvetica", 16, "bold"), bg="#ffffff"
        )
        title_label.pack(pady=(0, 8))

        self.status_label = tk.Label(
            wrapper, text="Status: Idle",
            font=("Helvetica", 11), bg="#ffffff"
        )
        self.status_label.pack(pady=(0, 8))

        # Buttons row
        btn_row = tk.Frame(wrapper, bg="#ffffff")
        btn_row.pack(pady=4)

        self.firmware_button = ttk.Button(
            btn_row, text="Firmware", command=self.download_firmware
        )
        self.firmware_button.grid(row=0, column=0, padx=6)

        self.effects_button = ttk.Button(
            btn_row, text="Effects", command=self.download_effects
        )
        self.effects_button.grid(row=0, column=1, padx=6)

        # Progress bar
        self.progress = ttk.Progressbar(wrapper, mode="determinate", length=360)
        self.progress.pack(pady=(10, 4))
        self.progress["value"] = 0
        self.progress["maximum"] = 100

        # Last saved file (read-only)
        tk.Label(wrapper, text="Last file:", bg="#ffffff").pack(anchor="w")
        self.last_file_var = tk.StringVar(value="(none)")
        last_entry = tk.Entry(wrapper, textvariable=self.last_file_var, state="readonly")
        last_entry.pack(fill="x", pady=(0, 8))

        # Simple log box
        tk.Label(wrapper, text="Log:", bg="#ffffff").pack(anchor="w")
        self.log = tk.Text(wrapper, height=10)
        self.log.pack(fill="both", expand=True)
        self._log("Ready.")

    # --------- helpers ----------
    def _log(self, msg: str):
        self.log.insert("end", msg + "\n")
        self.log.see("end")

    def set_status(self, text: str):
        self.status_label.config(text=text)
        self._log(text)

    def list_server_files(self, server_url):
        """
        Simple: JSON list or plaintext (one filename per line).
        """
        try:
            r = requests.get(server_url, timeout=8)
            r.raise_for_status()
            # Try JSON
            try:
                data = r.json()
                if isinstance(data, list):
                    return [str(x) for x in data]
            except Exception:
                pass
            # Plaintext lines fallback
            text = r.text.strip()
            files = [ln.strip() for ln in text.splitlines() if ln.strip()]
            return files
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Failed to fetch file list:\n{e}")
            return []

    def pick_file_from_list(self, title, files):
        if not files:
            return None
        default = files[0]
        user_choice = simpledialog.askstring(
            title,
            "Available files:\n" + "\n".join(files) + f"\n\nType the file name:\n(Default: {default})"
        )
        if user_choice is None or user_choice.strip() == "":
            return default
        if user_choice not in files:
            messagebox.showwarning("Not found", "That file is not in the list.")
            return None
        return user_choice

    def download_one(self, base_url, file_name, save_path):
        try:
            url = f"{base_url.rstrip('/')}/{file_name}"
            with requests.get(url, stream=True, timeout=12) as r:
                r.raise_for_status()
                total = int(r.headers.get("Content-Length", "0"))
                downloaded = 0

                with open(save_path, "wb") as out:
                    for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                        if not chunk:
                            continue
                        out.write(chunk)
                        downloaded += len(chunk)
                        pct = int(downloaded * 100 / total) if total else 0
                        self.progress["value"] = pct
                        self.root.update_idletasks()

            self.set_status(f"Status: {file_name} downloaded successfully.")
            self.last_file_var.set(save_path)
            messagebox.showinfo("Success", f"Saved '{file_name}' to:\n{save_path}")
        except requests.exceptions.RequestException as e:
            self.set_status("Status: Download failed.")
            messagebox.showerror("Error", f"Failed to download file:\n{e}")

    def choose_save_path(self, suggested_name):
        if not suggested_name.lower().endswith(DEFAULT_SAVE_EXT):
            suggested_name += DEFAULT_SAVE_EXT
        return filedialog.asksaveasfilename(
            title="Save As",
            initialfile=suggested_name,
            defaultextension=DEFAULT_SAVE_EXT,
            filetypes=[("Bin files", f"*{DEFAULT_SAVE_EXT}"), ("All files", "*.*")]
        )

    # --------- actions ----------
    def download_firmware(self):
        files = self.list_server_files(FIRMWARE_URL)
        if not files:
            return
        selected = self.pick_file_from_list("Firmware Files", files)
        if not selected:
            return
        save_path = self.choose_save_path(selected)
        if not save_path:
            self.set_status("Status: Download canceled.")
            return
        self.progress["value"] = 0
        self.set_status(f"Status: Downloading {selected} ...")
        self.download_one(FIRMWARE_URL, selected, save_path)

    def download_effects(self):
        files = self.list_server_files(EFFECTS_URL)
        if not files:
            return
        selected = self.pick_file_from_list("Effects Files", files)
        if not selected:
            return
        save_path = self.choose_save_path(selected)
        if not save_path:
            self.set_status("Status: Download canceled.")
            return
        self.progress["value"] = 0
        self.set_status(f"Status: Downloading {selected} ...")
        self.download_one(EFFECTS_URL, selected, save_path)

# ---- main ----
if __name__ == "__main__":
    root = tk.Tk()
    try:
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")
    except Exception:
        pass
    app = UpdaterApp(root)
    root.mainloop()

