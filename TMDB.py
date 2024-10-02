import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os
import shutil
from urllib.request import urlopen
import textwrap
from typing import List, Dict, Tuple
import ShieldShare

# Constants
API_URL = "https://api.themoviedb.org/3/"
API_HEADERS = {
    "accept": "application/json",
    "Authorization": "Bearer TOKEN"  # Replace with your token
}
TRUETYPE_URL = 'https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Light.ttf'
BACKGROUND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tmdb_backgrounds")

# Edit to True if you want to automatically share the images with your Android TV device
SHARE_TO_TV = False

# Edit to set the number of pages, which dictates the amount of wallpapers generated
# Each page has 20 items
# Setting either option to 0 won't generate wallpapers for said option, in case you only want movies or only tv shows
num_pages_movies = 1
num_pages_tvshows = 1

# Ensure the output folder exists
os.makedirs(BACKGROUND_DIR, exist_ok=True)

def fetch_trending(url: str, num_pages: int = 1) -> List[Dict]:
    """Fetches trending movies or TV shows."""
    all_results = []
    for page in range(1, num_pages + 1):
        response = requests.get(f"{url}&page={page}", headers=API_HEADERS)
        response.raise_for_status()  # Raise error for bad responses
        all_results.extend(response.json().get('results', []))
    return all_results

def fetch_genres(media_type: str) -> Dict[int, str]:
    """Fetches genres for movies or TV shows."""
    genres_url = f'{API_URL}genre/{media_type}/list?language=en-US'
    response = requests.get(genres_url, headers=API_HEADERS)
    response.raise_for_status()
    return {genre['id']: genre['name'] for genre in response.json().get('genres', [])}

def fetch_details(media_type: str, media_id: int) -> Dict:
    """Fetches details of a movie or TV show."""
    details_url = f'{API_URL}{media_type}/{media_id}?language=en-US'
    response = requests.get(details_url, headers=API_HEADERS)
    response.raise_for_status()
    return response.json()

def resize_image(image: Image.Image, height: int) -> Image.Image:
    """Resizes an image to a specified height while maintaining aspect ratio."""
    ratio = height / image.height
    width = int(image.width * ratio)
    return image.resize((width, height))

def clean_filename(filename: str) -> str:
    """Cleans a filename to ensure it's safe for the filesystem."""
    return "".join(c if c.isalnum() or c in "._-" else "_" for c in filename)

def draw_text(draw: ImageDraw.Draw, position: Tuple[int, int], text: str, font: ImageFont.ImageFont, shadow_color: str, main_color: str, shadow_offset: int = 2):
    """Draws text with shadow effect."""
    draw.text((position[0] + shadow_offset, position[1] + shadow_offset), text, font=font, fill=shadow_color)
    draw.text(position, text, font=font, fill=main_color)
        
def process_image(image_url, title, overview, is_movie, genre, year, rating, duration=None, seasons=None):
    """
    Processes and saves an image.

    Parameters:
        image_url (str): URL of the image.
        title (str): Title of the movie or TV show.
        is_movie (bool): True if the media is a movie, False if it's a TV show.
        genre (str): Genre of the movie or TV show.
        year (str): Release year of the movie or TV show.
        rating (float): Rating of the movie or TV show.
        duration (str, optional): Duration of the movie. Defaults to None.
        seasons (int, optional): Number of seasons of the TV show. Defaults to None.
    """
    response = requests.get(image_url, timeout=10)
    if response.status_code == 200:
        # Open the downloaded image
        image = Image.open(BytesIO(response.content))
        # Resize the image
        image = resize_image(image, 1500)
        # Open background, overlay, and TMDB logo images
        bckg = Image.open(os.path.join(os.path.dirname(__file__), "bckg.png"))
        overlay = Image.open(os.path.join(os.path.dirname(__file__), "overlay.png"))
        tmdblogo = Image.open(os.path.join(os.path.dirname(__file__), "tmdblogo.png"))
        
        # Paste the image onto the background
        bckg.paste(image, (1175, 0))
        bckg.paste(overlay, (1175, 0), overlay)
        bckg.paste(tmdblogo, (680, 975), tmdblogo)
        draw = ImageDraw.Draw(bckg)
        
        # Define fonts and colors
        font_title = ImageFont.truetype(urlopen(TRUETYPE_URL), size=190)
        font_overview = ImageFont.truetype(urlopen(TRUETYPE_URL), size=45)
        font_custom = ImageFont.truetype(urlopen(TRUETYPE_URL), size=60)
        shadow_color = "black"
        main_color = "white"
        overview_color = (150,150,150)
        metadata_color = "white"
        shadow_offset = 2
        
        # Define text positions
        title_position = (200, 540)
        overview_position = (210, 830)
        info_position = (210, 520)
        custom_position = (210, 950)

        # Draw title
        draw.text((title_position[0] + shadow_offset, title_position[1] + shadow_offset), title, font=font_title, fill=shadow_color)
        draw.text(title_position, title, font=font_title, fill=main_color)
        
        # Wrap overview text
        wrapped_overview = "\n".join(textwrap.wrap(overview,width= 90,initial_indent= "",subsequent_indent= "",expand_tabs= True,tabsize= 8,replace_whitespace= True,fix_sentence_endings= False,break_long_words= True,break_on_hyphens= True,drop_whitespace= True,max_lines= 2,placeholder= " ..."))
        
        # Draw overview
        draw.text((overview_position[0] + shadow_offset, overview_position[1] + shadow_offset), wrapped_overview, font=font_overview, fill=shadow_color)
        draw.text(overview_position, wrapped_overview, font=font_overview, fill=overview_color)
        
        # Determine genre text and additional info
        genre_text = genre
        additional_info = duration if is_movie else f"{seasons} {'Season' if seasons == 1 else 'Seasons'}"
        rating_text = f"TMDB: {rating}"
        year_text = f"{year[5:7]}-{year[:4]}"
        info_text = f"{genre_text}  •  {year_text}  •  {additional_info}  •  {rating_text}"
        
        # Draw metadata
        draw.text((info_position[0] + shadow_offset, info_position[1] + shadow_offset), info_text, font=font_overview, fill=shadow_color)
        draw.text(info_position, info_text, font=font_overview, fill=overview_color)
        
        # Draw custom text
        draw.text((custom_position[0] + shadow_offset, custom_position[1] + shadow_offset), "Now Trending on", font=font_custom, fill=shadow_color)
        draw.text(custom_position, "Now Trending on", font=font_custom, fill=metadata_color)
        
        # Save the resized image
        filename = os.path.join(BACKGROUND_DIR, f"{clean_filename(title)}.jpg")
        bckg = bckg.convert('RGB')
        bckg.save(filename)
        print(f"Image saved: {filename}")
    else:
        print(f"Failed to download background for {title}")


def process_media(current_media: List[Dict], is_movie: bool, genres: Dict[int, str]):
    """Processes and saves media images (movies or TV shows)."""
    for media in current_media:
        title = media['title'] if is_movie else media['name']
        overview = media['overview']
        cleaned_title = clean_filename(title)
        backdrop_path = media.get('backdrop_path')

        if backdrop_path:
            image_url = f"https://image.tmdb.org/t/p/original{backdrop_path}"
            if f"{cleaned_title}.jpg" not in existing_files:
                if is_movie:
                    movie_details = fetch_details("movie", media['id'])
                    duration = movie_details.get('runtime', "N/A")
                    if duration != "N/A":
                        hours = duration // 60
                        minutes = duration % 60
                        duration = f"{hours}h{minutes}min"
                    genre_text = ', '.join(genres[genre_id] for genre_id in media['genre_ids'])
                    process_image(image_url, title, overview, is_movie, genre_text, 
                                  media.get('release_date', ""), 
                                  round(media['vote_average'], 1), 
                                  duration)
                else:
                    tv_details = fetch_details("tv", media['id'])
                    seasons = tv_details.get('number_of_seasons', 0)
                    genre_text = ', '.join(genres[genre_id] for genre_id in media['genre_ids'])
                    process_image(image_url, title, overview, is_movie, genre_text, 
                                  media.get('first_air_date', ""), 
                                  round(media['vote_average'], 1), 
                                  seasons=seasons)
                

def get_current_trending() -> Tuple[List[Dict], List[Dict]]:
    """Gets the current trending movies and TV shows."""
    current_movies = fetch_trending(f"{API_URL}trending/movie/week?language=en-US", num_pages_movies)
    current_tvshows = fetch_trending(f"{API_URL}trending/tv/week?language=en-US", num_pages_tvshows)
    return current_movies, current_tvshows

# Get current trending media
current_movies, current_tvshows = get_current_trending()
existing_files = set(os.listdir(BACKGROUND_DIR))

# Process movies
process_media(current_movies, is_movie=True, genres=fetch_genres("movie"))

# Process TV shows
process_media(current_tvshows, is_movie=False, genres=fetch_genres("tv"))

# Remove files that are no longer in the current trending lists
current_titles = {clean_filename(media['title']) if 'title' in media else clean_filename(media['name']) for media in current_movies + current_tvshows}

for file_name in existing_files:
    if file_name[:-4] not in current_titles:  # Exclude the .jpg extension for comparison
        os.remove(os.path.join(BACKGROUND_DIR, file_name))
        print(f"Removed unused file: {file_name}")

# Share to Android TV folder
if(SHARE_TO_TV):
    ShieldShare.sync_folders(BACKGROUND_DIR)
