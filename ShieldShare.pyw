import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os
import shutil
from urllib.request import urlopen
import textwrap
from typing import List, Dict, Tuple

# For this to work, you need to toggle on the option to transfer files over network on your Shield device
# Under: settings > device preferences > storage > transfer files over local network

SHIELD_FOLDER = r"\\YOUR SHIELD IP\internal\Pictures\Synced Wallpapers" # Replace with the IP address of your shield

# Sync with Nvidia Shield folder
def sync_folders(background_dir):
    # Ensure the target folder exists
    if not os.path.exists(SHIELD_FOLDER):
        os.makedirs(SHIELD_FOLDER)

    # Copy new/updated files from background_dir to shield_folder
    shutil.copytree(background_dir, SHIELD_FOLDER, dirs_exist_ok=True)

    # Get the list of files in both the output and shield folders
    output_files = set(os.listdir(background_dir))
    shield_files = set(os.listdir(SHIELD_FOLDER))

    # Remove files from shield_folder that no longer exist in background_dir
    for file_name in shield_files:
        if file_name not in output_files:
            shield_file_path = os.path.join(SHIELD_FOLDER, file_name)
            if os.path.isfile(shield_file_path):
                os.remove(shield_file_path)