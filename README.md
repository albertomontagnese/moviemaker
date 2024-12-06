# To run

pip install 
python moviemaker.py

I'm creating a huge video from all the .mp4 videos ( only mp4 videos ) in the folder ./assets/videos
don't use this file if its resolution height is less than VIDEO_RESOLUTION_HEIGHT
Then I'll split it into multiple videos and add text and outro to each one of them, which will show in the output folder ./output/

# PARAMETERS ------------------------------------------------

def get_default_params():
    return {
        'is_test': False,
        'total_length_before_outro': 12,
        'add_outro': False,
        'add_music': True,
        'music_directory': './assets/music',
        'add_text': True,
        'main_title': "",
        'video_resolution_width': 720,
        'strings_location': "facts.csv",
        'video_title_folder': './output/',
        'main_title_font_type': './assets/fonts/albas.ttf',
        'fact_font_type': './assets/fonts/AspireDemibold-YaaO.ttf',
        'base_video_file_name': 'Affirmative',
        'max_hashtags_length': 120,
        'text_font_weight': 3,
        'text_1_key': "TEXT_1",
        'text_2_key': "TEXT_2"
    }

# Derived parameters

VIDEO_RESOLUTION_HEIGHT = params['video_resolution_width'] * 16/9
MARGIN_TOP = int(divmod(params['video_resolution_width'] * 0.275, 1)[0])
OUTRO = VideoFileClip('./assets/outro/outro.mp4')
OUTRO_DURATION = OUTRO.duration