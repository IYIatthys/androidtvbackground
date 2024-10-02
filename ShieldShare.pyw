import os
import shutil

# For this to work, you need to toggle on the option to transfer files over network on your Shield device
# Under: settings > device preferences > storage > transfer files over local network

SHIELD_FOLDER = r"\\YOUR SHIELD IP\internal\Pictures\Synced Wallpapers"  # Replace with the IP address of your Shield

# Sync with Nvidia Shield folder
def sync_folders(background_dir):
    # First, check if SHIELD_FOLDER is accessible
    try:
        if not os.path.exists(SHIELD_FOLDER):
            # Attempt to create the folder if it doesn't exist
            os.makedirs(SHIELD_FOLDER)
    except OSError as e:
        # If the folder isn't accessible, abort sync
        print(f"Error accessing Shield folder: {e}")
        print("Sync aborted.")
        return

    # Copy new/updated files from background_dir to SHIELD_FOLDER
    shutil.copytree(background_dir, SHIELD_FOLDER, dirs_exist_ok=True)

    # Get the list of files in both the output and Shield folders
    output_files = set(os.listdir(background_dir))
    shield_files = set(os.listdir(SHIELD_FOLDER))

    # Remove files from SHIELD_FOLDER that no longer exist in background_dir
    for file_name in shield_files:
        if file_name not in output_files:
            shield_file_path = os.path.join(SHIELD_FOLDER, file_name)
            if os.path.isfile(shield_file_path):
                os.remove(shield_file_path)
                print(f"Removed unused file from Shield: {file_name}")
