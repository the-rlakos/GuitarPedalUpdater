# Guitar Pedal Updater

A small Tkinter app to download **firmware** or **effects** from a local server and save them to disk.

## 🧰 Requirements
```bash
pip install requests pillow   # pillow only if you want the background image
```

## ▶️ Run
```bash
python updater_app.py
```

## 🔧 Configure
At the top of `updater_app.py`:
- `FIRMWARE_URL` (default: http://localhost:8000/firmware)
- `EFFECTS_URL`  (default: http://localhost:8000/effects)
- `DEFAULT_SAVE_EXT` (default: .bin)

## 🖼 Optional
Place a `tones_background.png` next to the script to show a background image.

## 💡 How it works
1. Click **Firmware** or **Effects**  
2. Pick a file from the server-provided list  
3. Choose where to save  
4. Watch the progress bar → Done ✅
