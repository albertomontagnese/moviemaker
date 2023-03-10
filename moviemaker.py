from moviepy.editor import *    
import os
import numpy as np
from moviepy.video.fx.all import crop
import constants
import random
import glob

IS_TEST = False
TOTAL_LENGTH_BEFORE_OUTRO = 10
ADD_OUTRO = True
ADD_MUSIC = True
ADD_TEXT = True
OUTRO = VideoFileClip('./assets/outro/outro.mp4')
OUTRO_DURATION = OUTRO.duration
VIDEO_RESOLUTION_WIDTH = 720
VIDEO_RESOLUTION_HEIGHT = VIDEO_RESOLUTION_WIDTH * 16/9
MARGIN_TOP = int(divmod(VIDEO_RESOLUTION_WIDTH * 0.275, 1)[0])


def get_facts():
    # remove duplicates and store value in facts again
    facts = list({v['question']:v for v in constants.all_facts}.values())
    return facts


def get_hashtag_from_fact(fact_index, max_chars=120):
    facts = get_facts()
    fact = facts[fact_index]["answer"]
    # remove QUANTITY and DATE entities
    all_entities = [entity for entity in constants.comprehend_entities if entity["Type"] != "QUANTITY" and entity["Type"] != "DATE"]
    # loop through all the entities and find the ones whose Text are in the fact
    entities = [entity for entity in all_entities if entity["Text"] in fact]
    # create an hashtags array with the entities Text. Keep in mind a Text can have multiple words, so we need to split it by space and add a # in front of each word
    hashtags = []
    for entity in entities:
        words = entity["Text"].split(" ")
        for word in words:
            hashtags.append("#" + word)
    # remove duplicates
    hashtags = list(set(hashtags))
    if len(hashtags) < 5:
        hashtags.append("#funfacts")
        hashtags.append("#didyouknow")
        hashtags.append("#travel")
        hashtags.append("#traveltiktok")
        hashtags.append("#interesting")
    
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
    x1 = (w - VIDEO_RESOLUTION_WIDTH)//2
    x2 = (w + VIDEO_RESOLUTION_WIDTH)//2
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
    
    is_light = np.mean(frame) > 127
    font_color = is_light and "black" or "white"
    red_color = (255, 0, 0)
    green_color = (0, 255, 0)
    bg_color = is_question and red_color or green_color
    font_type = './assets/fonts/test.ttf'
    text_clip = TextClip(txt=text,
                        size=(0.875 * VIDEO_RESOLUTION_WIDTH, VIDEO_RESOLUTION_WIDTH / 2),
                        font=font_type,
                        color=font_color,
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

    print("Adding text to the video number " + str(fact_index) + "), Fact question: " + facts[fact_index]["question"]) 
    # add text to the video, the text has a black background and a white color
    
    # get a random font_type from the fonts folder ./assets/fonts
    # font_type = random.choice(glob.glob("./assets/fonts/*.ttf"))
    # print("font_type: " + font_type)

    font_type = './assets/fonts/albas.ttf'
    
    
    txt_clip = TextClip(" DID YOU KNOW? ", fontsize=50, color='white', font=font_type)
    txt_clip = txt_clip.on_color(size=(txt_clip.w+10,txt_clip.h+10), color=(0,0,0), pos=('center','center'), col_opacity=1)
    txt_clip = txt_clip.set_pos(('center','top'))
    txt_clip = txt_clip.margin(top=MARGIN_TOP, opacity=0) # (optional) logo-border padding
    txt_clip = txt_clip.set_duration(TOTAL_LENGTH_BEFORE_OUTRO)

    
    random_str2 = facts[fact_index]["question"] + "..." 
    frame = final_clip.get_frame(0)
    txt_clip2 = generate_text_label(random_str2, True,frame)
    txt_clip2 = txt_clip2.set_duration(TOTAL_LENGTH_BEFORE_OUTRO/2)
    final_clip = CompositeVideoClip([final_clip, txt_clip2]) 

    random_str3 = "..." + facts[fact_index]["answer"]
    frame = final_clip.get_frame(TOTAL_LENGTH_BEFORE_OUTRO/2)
    txt_clip3 = generate_text_label(random_str3, False, frame)
    txt_clip3 = txt_clip3.set_duration(TOTAL_LENGTH_BEFORE_OUTRO/2)
    txt_clip3 = txt_clip3.set_start(TOTAL_LENGTH_BEFORE_OUTRO/2)
    final_clip = CompositeVideoClip([final_clip, txt_clip3]) 




    
    final_clip = CompositeVideoClip([final_clip, txt_clip]) 

    return final_clip


# MAIN CODE ------------------------------------------------


# IS_TEST = True
# TOTAL_LENGTH_BEFORE_OUTRO = 2 
# ADD_OUTRO = False
# ADD_MUSIC = False
# ADD_TEXT = True

# generate_text_label("test", True)
# TODO reactivate this:
video_dir = IS_TEST and './assets/videos2' or './assets/videos'
print("Generating video from all videos in the folder " + video_dir)
final_clip = get_final_clip_from_videos(video_dir)
print("Generated video, total duration: " + str(final_clip.duration))

final_music = None
if (ADD_MUSIC):
    audio_dir = './assets/music'
    # concatenate all the music files in the folder ./assets/music 
    music_files = os.listdir(audio_dir)
    # remove those that are not .mp3
    music_files = [file for file in music_files if file.endswith('.mp3')]
    music_clips = [AudioFileClip(audio_dir + '/' + file) for file in music_files]
    final_music = concatenate_audioclips(music_clips)

print("Splitting into multiple videos and adding text and outro")
for i in range(int(final_clip.duration / TOTAL_LENGTH_BEFORE_OUTRO)):
    cur_clip = final_clip.subclip(TOTAL_LENGTH_BEFORE_OUTRO*i, TOTAL_LENGTH_BEFORE_OUTRO*(i+1))
    if (ADD_TEXT):
        all_facts = get_facts()
        cur_clip = add_text(cur_clip, all_facts, i)
    if (ADD_OUTRO):
        cur_clip = concatenate_videoclips([cur_clip, OUTRO], method="compose")
        
    print("Adding music")
    # add the music
    if (ADD_MUSIC):
        cur_clip =  add_music(final_music, cur_clip)
        cur_clip = cur_clip.audio_fadeout(OUTRO_DURATION + 1)


    max_title_length = 150
    video_title_folder = './output/'
    video_title_no_ext = 'GlobetrotterChronicles ' + str(i + 1) + " "
    video_title_no_ext += get_facts()[i]["question"] + " "
    if len(video_title_no_ext) < max_title_length:
        video_title_no_ext += get_hashtag_from_fact(i, max_title_length - len(video_title_no_ext))
    video_title = video_title_folder + video_title_no_ext
    
    if not video_title.endswith('.mp4'):
        video_title += '.mp4'

    cur_clip.write_videofile(video_title, fps=24, codec='libx264', audio_codec='aac')






