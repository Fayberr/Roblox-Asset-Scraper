# Roblox Asset Scraper

Download Roblox assets easily. Supports:

- Single asset download by asset ID  
- Bulk download from a list of asset IDs in a file (`assets.txt`)  
- Download all decals from a Roblox user profile by user ID  

## Features

- Saves assets as PNG files with proper names  
- Prevents duplicate filenames by adding suffixes  
- Shows progress during downloads  
- Warns if the user inventory is private  
- Organizes downloads in folders by mode and count  

## Usage

Run the script and choose the mode:

```bash
python rblx_scraper.py
```

## Requirements

- Python 3.x
- Request Library
- tqdm library for progress bar

Install dependencies with:

```bash
pip install requests tqdm
```
