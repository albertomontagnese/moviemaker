from moviepy.editor import *    
import os
import numpy as np
from moviepy.video.fx.all import crop
import constants
import time
import pandas as pd


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

# Global variables initialized with default values
params = get_default_params()

# Initialize derived parameters
VIDEO_RESOLUTION_HEIGHT = params['video_resolution_width'] * 16/9
MARGIN_TOP = int(divmod(params['video_resolution_width'] * 0.275, 1)[0])
OUTRO = VideoFileClip('./assets/outro/outro.mp4')
OUTRO_DURATION = OUTRO.duration

def set_params(new_params=None):
    global params, VIDEO_RESOLUTION_HEIGHT, MARGIN_TOP
    if new_params:
        params.update(new_params)
    
    # Update derived parameters
    VIDEO_RESOLUTION_HEIGHT = params['video_resolution_width'] * 16/9
    MARGIN_TOP = int(divmod(params['video_resolution_width'] * 0.275, 1)[0])

def get_facts():
    facts = pd.read_csv(params['strings_location'])
    # keep in mind that the first row is the header
    facts = facts.iloc[1:]  
    return facts


def get_hashtag_from_fact(fact_index, max_chars=params['max_hashtags_length']):
    facts = get_facts()
    # Split the hashtags string on spaces to get a list of hashtags
    hashtags = facts.iloc[fact_index]["HASHTAGS"].split(" ")
    
    if len(hashtags) < 5:
        hashtags.extend(["#affirmation", "#affirmative", "#affirmativefacts", 
                        "#affirmativequotes", "#affirmativeme"])
    
    while len(" ".join(hashtags)) > max_chars:
        hashtags.pop()
    return " ".join(hashtags)
    
    
def crop_outro():
    # doesnt work
    print("Cropping the outro to 9:16 ratio")
    clip = VideoFileClip("./assets/outro/outro.mp4")
    clip = crop_to_9_16(clip)
    clip.write_videofile("./assets/outro/outro.mp4", codec='libx264', audio_codec='aac')

def crop_to_9_16(clip):
    (w, h) = clip.size
    x1 = (w - params['video_resolution_width'])//2
    x2 = (w + params['video_resolution_width'])//2
    y1 = (h - VIDEO_RESOLUTION_HEIGHT)//2
    y2 = (h + VIDEO_RESOLUTION_HEIGHT)//2
    clip = crop(clip, x1=x1, y1=y1, x2=x2, y2=y2)

    if (h < VIDEO_RESOLUTION_HEIGHT ):
        print("\033[91m ERROR!!! : Video height is less than 16:9 ratio \033[0m")


    return clip
    




    # (w, h) = clip.size
    # crop_width = h * 9/16
    # x1, x2 = (w - crop_width)//2, (w+crop_width)//2
    # y1, y2 = 0, h
    # clip = crop(clip, x1=x1, y1=y1, x2=x2, y2=y2)
    # return clip



def get_final_clip_from_videos(video_dir):
    files = os.listdir(video_dir)
    # remove those that are not .mp4
    files = [file for file in files if file.endswith('.mp4')]

    files.sort()
    # clips = [VideoFileClip(video_dir + '/' + file) for file in files]

    # refactor above to use normal loop 
    clips = []
    for file in files:
        clip = VideoFileClip(video_dir + '/' + file)
        # don't use this file if its resolution height is less than VIDEO_RESOLUTION_HEIGHT
        if clip.size[1] < VIDEO_RESOLUTION_HEIGHT:
            continue
        clip = crop_to_9_16(clip)
        clips.append(clip)

    final_clip = concatenate_videoclips(clips, method="compose")

    return final_clip

def add_music(final_music, final_clip):
    
    clip_duration = final_clip.duration
    start_time = np.random.randint(0, final_music.duration - clip_duration)
    final_music = final_music.subclip(start_time, start_time + clip_duration)


    final_clip = final_clip.set_audio(final_music)
    return final_clip

def generate_text_label(text, is_question, frame):
    # Check if frame is an ImageClip (test case) or regular video frame
    if isinstance(frame, ImageClip):
        frame_array = frame.get_frame(0)
    else:
        frame_array = frame
    is_light = np.mean(frame_array) > 127
    font_color = is_light and "black" or "white"
    stroke_color = font_color
    red_color = (255, 0, 0)
    green_color = (0, 255, 0)
    bg_color = is_question and red_color or green_color
    font_type = params['fact_font_type']
    text_clip = TextClip(txt=text,
                        size=(0.875 * params['video_resolution_width'], params['video_resolution_width'] / 2),
                        font=font_type,
                        color=font_color,
                        stroke_color=stroke_color,
                        stroke_width=params['text_font_weight'],
                        kerning=-2, 
                        interline=-1, 
                        method='caption')
    text_clip = text_clip.set_position('bottom')
    text_clip = text_clip.margin(bottom=MARGIN_TOP, opacity=0)
    
    # if (IS_TEST):
    #     preview = CompositeVideoClip([frame, clip_to_overlay])
    #     preview.save_frame("out.png")
    return text_clip

def add_text(final_clip, facts, fact_index):
    fact_question = facts.iloc[fact_index][params['text_1_key']]
    fact_answer = facts.iloc[fact_index][params['text_2_key']]
    print("Adding text to the video number " + str(fact_index) + "), Fact question: " + fact_question)
    
    # Only add the "DID YOU KNOW?" title if ADD_TITLE is True
    if params['main_title']:
        font_type = params['main_title_font_type']
        txt_clip = TextClip(params['main_title'], fontsize=50, color='white', font=font_type)
        txt_clip = txt_clip.on_color(size=(txt_clip.w+10,txt_clip.h+10), color=(0,0,0), pos=('center','center'), col_opacity=1)
        txt_clip = txt_clip.set_pos(('center','top'))
        txt_clip = txt_clip.margin(top=MARGIN_TOP, opacity=0)
        txt_clip = txt_clip.set_duration(params['total_length_before_outro'])
    
    # Create question text clip (first half)
    frame = final_clip.get_frame(0)
    question_clip = generate_text_label(fact_question, True, frame)
    question_clip = question_clip.set_duration(params['total_length_before_outro']/2)
    
    # Create answer text clip (second half)
    answer_clip = generate_text_label(fact_answer, False, frame)
    answer_clip = answer_clip.set_start(params['total_length_before_outro']/2)  # Start at halfway point
    answer_clip = answer_clip.set_duration(params['total_length_before_outro']/2)
    
    # Combine clips
    final_clip = CompositeVideoClip([final_clip, question_clip, answer_clip])
    
    if params['main_title']:
        final_clip = CompositeVideoClip([final_clip, txt_clip])

    return final_clip

def process_videos():
    video_dir = params['is_test'] and './assets/videos2' or './assets/videos'
    print("--------------- IMPORTANT READ CAREFULLY ----------------")
    print("I'm creating a huge video from all the .mp4 videos ( only mp4 videos ) in the folder " + video_dir)
    print("don't use this file if its resolution height is less than VIDEO_RESOLUTION_HEIGHT")

    print(f"Then I'll split it into multiple videos and add text and outro to each one of them, which will show in the output folder {params['video_title_folder']}")    
    final_clip = get_final_clip_from_videos(video_dir)
    print(f"Generated base video clip of {final_clip.duration:.1f}s")

    final_music = None
    if (params['add_music']):
        # concatenate all the music files in the folder ./assets/music 
        music_files = os.listdir(params['music_directory'])
        music_files = [file for file in music_files if file.endswith('.mp3')]
        music_clips = [AudioFileClip(params['music_directory'] + '/' + file) for file in music_files]
        final_music = concatenate_audioclips(music_clips)

    print("Splitting into multiple videos and adding text and outro")
    num_videos = int(final_clip.duration / params['total_length_before_outro'])
    print(f"Will generate {num_videos} videos of {params['total_length_before_outro']} seconds each")
    print("Starting video generation...")

    start_time = time.time()

    for i in range(num_videos):
        video_start_time = time.time()
        print(f"\nProcessing video {i+1}/{num_videos}")
        
        cur_clip = final_clip.subclip(params['total_length_before_outro']*i, params['total_length_before_outro']*(i+1))
        if (params['add_text']):
            all_facts = get_facts()
            cur_clip = add_text(cur_clip, all_facts, i)
        if (params['add_outro']):
            cur_clip = concatenate_videoclips([cur_clip, OUTRO], method="compose")
            
        print("Adding music")
        # add the music
        if (params['add_music']):
            cur_clip =  add_music(final_music, cur_clip)
            cur_clip = cur_clip.audio_fadeout(OUTRO_DURATION + 1)


        max_title_length = 150
        video_title_no_ext = params['base_video_file_name'] + " " + str(i + 1) + " "
        # video_title_no_ext += get_facts()[i]["fact"] + " "
        video_title_no_ext += get_facts().iloc[i][params['text_1_key']] + " "
        if len(video_title_no_ext) < max_title_length:
            video_title_no_ext += get_hashtag_from_fact(i, max_title_length - len(video_title_no_ext))
        video_title = params['video_title_folder'] + video_title_no_ext
        
        if not video_title.endswith('.mp4'):
            video_title += '.mp4'

        cur_clip.write_videofile(video_title, fps=24, codec='libx264', audio_codec='aac')

        video_end_time = time.time()
        video_duration = round(video_end_time - video_start_time, 1)
        total_duration = round(video_end_time - start_time, 1)
        print(f"Video {i+1} completed in {video_duration}s (Total time elapsed: {total_duration}s)")

    print(f"\nAll {num_videos} videos generated successfully!")
    print(f"Total time taken: {round(time.time() - start_time, 1)}s")

# TEST FUNCTIONS ------------------------------------------------

# create just one frame of the video to test the text
def test_text_label():
    frame = ImageClip('./assets/pics/other/test.jpeg')
    txt_clip = get_facts().iloc[0][params['text_1_key']]  
    txt_clip = generate_text_label(txt_clip, True, frame)
    # Create a composite clip with both the background frame and text
    test_composite = CompositeVideoClip([frame, txt_clip])
    test_composite.save_frame("out.png")
    exit()


# MAIN CODE ------------------------------------------------

if __name__ == "__main__":
    
    # test 1
    # test_text_label()
    
    # main code
    process_videos()






