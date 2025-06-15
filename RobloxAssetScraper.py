import requests
import os
import time
from tqdm import tqdm

API_INVENTORY = "https://inventory.roproxy.com/v2/users/{}/inventory"
API_THUMBNAIL = "https://thumbnails.roblox.com/v1/assets"

BASE_DIRS = ["SingleScrapes", "MassScrapes", "ProfileScrapes"]

def sanitize_filename(name):
    return "".join(c for c in name if c.isalnum() or c in (" ", "_", "-")).strip()

def ensure_unique_filename(folder, base_name):
    name, ext = os.path.splitext(base_name)
    counter = 1
    candidate = base_name
    while os.path.exists(os.path.join(folder, candidate)):
        candidate = f"{name}_{counter}{ext}"
        counter += 1
    return candidate

def ensure_base_dirs():
    for d in BASE_DIRS:
        if not os.path.exists(d):
            os.makedirs(d)
            print(f"[+] Created base folder: {d}")

def get_folder_with_number(base_dir, base_name):
    counter = 0
    while True:
        suffix = f"_{counter}" if counter > 0 else ""
        folder = os.path.join(base_dir, f"{base_name}{suffix}")
        if not os.path.exists(folder):
            os.makedirs(folder)
            return folder
        counter += 1

def input_retry(prompt, valid_options=None):
    while True:
        val = input(prompt).strip().lower()
        if valid_options and val not in valid_options:
            print(f"Invalid input, choose one of: {valid_options}")
        else:
            return val

def get_decals_for_user(user_id):
    decals = []
    params = {"assetTypes": "Decal", "limit": 100, "sortOrder": "Asc"}
    next_token = ""
    while True:
        p = params.copy()
        if next_token:
            p["pageToken"] = next_token
        res = requests.get(API_INVENTORY.format(user_id), params=p)
        if res.status_code == 403 or res.status_code == 401:
            print("[!] Warning: Inventory is private or access denied.")
            return None
        if res.status_code != 200:
            print("[x] Failed to fetch inventory:", res.status_code)
            return None
        data = res.json().get("data", [])
        decals.extend(data)
        next_token = res.json().get("nextPageToken", "")
        if not next_token:
            break
        time.sleep(0.4)
    return decals

def download_asset(asset_id, name, folder):
    params = {"assetIds": asset_id, "size":"420x420","format":"Png","isCircular":"false"}
    r = requests.get(API_THUMBNAIL, params=params)
    if r.status_code != 200: return False
    url = r.json().get("data", [{}])[0].get("imageUrl")
    if not url: return False
    img = requests.get(url)
    if img.status_code == 200:
        safe_name = sanitize_filename(name)
        filename = f"{safe_name or asset_id}.png"
        filename = ensure_unique_filename(folder, filename)
        path = os.path.join(folder, filename)
        with open(path, "wb") as f:
            f.write(img.content)
        return True
    return False

def profile_mode():
    user_id = input("Profile ID: ").strip()
    res = requests.get(f"https://users.roblox.com/v1/users/{user_id}")
    if res.status_code == 200:
        username = res.json().get("name", f"profile{user_id}")
    else:
        username = f"profile{user_id}"
    print(f"\u2794 Fetching details from {username}...")
    decals = get_decals_for_user(user_id)
    if decals is None:
        print("Aborting due to private inventory or error.")
        return
    folder = get_folder_with_number("ProfileScrapes", username)
    print(f"✅ {len(decals)} decals found, downloading...")
    for d in tqdm(decals, desc="Downloading Decals", unit="asset"):
        aid = d["assetId"]
        name = d.get("name","")
        download_asset(aid, name, folder)

def single_mode():
    folder = get_folder_with_number("SingleScrapes", "Single")
    while True:
        asset_id = input("Asset ID: ").strip()
        if not asset_id.isdigit():
            print("Please enter a valid number.")
            continue
        name = input("Name for asset (optional): ").strip()
        if not name:
            name = asset_id
        print("Downloading...")
        if download_asset(asset_id, name, folder):
            print("✓ Download successful")
        else:
            print("✗ Download failed")
        if input_retry("Another asset? (y/n): ", ["y","n"]) == "n":
            break

def mass_mode():
    folder = get_folder_with_number("MassScrapes", "Mass")
    try:
        with open("assets.txt","r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("assets.txt not found.")
        return
    asset_ids = [line.strip() for line in lines if line.strip().isdigit()]
    print(f"Starting download of {len(asset_ids)} assets...")
    for aid in tqdm(asset_ids, desc="Downloading Assets", unit="asset"):
        download_asset(aid, aid, folder)
        time.sleep(0.3)

def main():
    ensure_base_dirs()
    mode = input_retry("Mode? (single/mass/profile): ", ["single","mass","profile"])
    if mode == "profile":
        profile_mode()
    elif mode == "single":
        single_mode()
    elif mode == "mass":
        mass_mode()

if __name__=="__main__":
    main()
