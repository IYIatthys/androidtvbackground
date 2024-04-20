import requests
import os
import time
from PIL import Image, ImageDraw, ImageFont  # Import Image module
from io import BytesIO
from urllib.request import urlopen

truetype_url = 'https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Light.ttf'

from plexapi.server import PlexServer

# Set the order_by parameter to 'aired' or 'added'
order_by = 'aired'
download_movies = True
download_series = True
# Set the number of latest movies to download
limit = 3

def resize_image(image, height):
    ratio = height / image.height
    width = int(image.width * ratio)
    return image.resize((width, height))

def download_latest_media(order_by, limit, media_type):
    baseurl = 'http://XXX:32400'
    token = 'XXX'
    plex = PlexServer(baseurl, token)

# Create a directory to save the backgrounds
    background_dir = f"{media_type}_backgrounds"
    os.makedirs(background_dir, exist_ok=True)

    if media_type == 'movie' and download_movies:
        media_items = plex.library.search(libtype='movie')
    elif media_type == 'tv' and download_series:
        media_items = plex.library.search(libtype='show')
    else:
        print("Invalid media_type parameter.")
        return
    
    if order_by == 'aired':
        media_sorted = sorted(media_items, key=lambda x: x.originallyAvailableAt, reverse=True)
    elif order_by == 'added':
        media_sorted = sorted(media_items, key=lambda x: x.addedAt, reverse=True)
    else:
        print("Invalid order_by parameter. Please use 'aired' or 'added'.")
        return

    for item in media_sorted[:limit]:
        print(item.title)
        # Get the URL of the background image
        background_url = item.artUrl

        if background_url:
            try:
                # Download the background image with a timeout of 10 seconds
                response = requests.get(background_url, timeout=10)
                if response.status_code == 200:
                    # Remove problematic characters from the item title
                    filename_safe_title = item.title.replace(':', '_')
                    # Save the background image to a file
                    background_filename = os.path.join(background_dir, f"{filename_safe_title}_background.jpg")
                    with open(background_filename, 'wb') as f:
                        f.write(response.content)
                    
                    # Open the background image with PIL
                    image = Image.open(background_filename)
                    
                    # Resize the image to have a height of 1080 pixels
                    image = resize_image(image, 1080)
                    
                    # Open overlay image
                    overlay = Image.open(os.path.join(os.path.dirname(__file__),"overlay.png"))
                    image.paste(overlay, (0, 0), overlay)

                    # Add text on top of the image with shadow effect
                    draw = ImageDraw.Draw(image)
                    font_title = ImageFont.truetype(urlopen(truetype_url), size=100)
                    font_info = ImageFont.truetype(urlopen(truetype_url), size=35)
                    title_text = f"{item.title}"
                    info_text = "Available now on Plex"
                    title_text_width, title_text_height = draw.textlength(title_text, font=font_title), draw.textlength(title_text, font=font_title)
                    info_text_width, info_text_height = draw.textlength(info_text, font=font_info), draw.textlength(info_text, font=font_info)
                    title_position = (100, 500)
                    info_position = (100, 615)
                    shadow_offset = 1
                    shadow_color = "black"
                    main_color = "white"
                    # Draw shadow for title
                    draw.text((title_position[0] + shadow_offset, title_position[1] + shadow_offset), title_text, font=font_title, fill=shadow_color)
                    # Draw main title text
                    draw.text(title_position, title_text, font=font_title, fill=main_color)
                    # Draw shadow for info
                    draw.text((info_position[0] + shadow_offset, info_position[1] + shadow_offset), info_text, font=font_info, fill=shadow_color)
                    # Draw main info text
                    draw.text(info_position, info_text, font=font_info, fill=main_color)
                    
                    # Save the modified image
                    image.save(background_filename)
                    
                    print(f"Background saved: {background_filename}")
                else:
                    print(f"Failed to download background for {item.title}")
            except Exception as e:
                print(f"An error occurred while processing {item.title}: {e}")
        else:
            print(f"No background image found for {item.title}")

        # Adding a small delay to give the server some time to respond
        time.sleep(1)

# Download the latest movies according to the specified order and limit
if download_movies:
    download_latest_media(order_by, limit, 'movie')

# Download the latest TV series according to the specified order and limit
if download_series:
    download_latest_media(order_by, limit, 'tv')
