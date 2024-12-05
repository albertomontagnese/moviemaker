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
ADD_IMAGE = True
OUTRO = VideoFileClip('./assets/outro/outro.mp4')
OUTRO_DURATION = OUTRO.duration
VIDEO_RESOLUTION_WIDTH = 720
VIDEO_RESOLUTION_HEIGHT = VIDEO_RESOLUTION_WIDTH * 16/9
MARGIN_TOP = int(divmod(VIDEO_RESOLUTION_WIDTH * 0.275, 1)[0])


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

    # files.sort()
    random.shuffle(files)

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
        break

    final_clip = concatenate_videoclips(clips, method="compose")


    # Add dark overlay
    from skimage.filters import gaussian


    # def blur(image):
    #     """ Returns a blurred (radius=2 pixels) version of the image """
    #     return gaussian(image.astype(float), sigma=9)

    def blur(image):
        blurred_frame = gaussian(image.astype(float), sigma=7)

        # Darken the blurred frame
        # darken_factor = 0.1
        # darkened_frame = (blurred_frame * darken_factor).astype(image.dtype)


        return blurred_frame

    
    final_clip = final_clip.fl_image( blur )

    return final_clip

def add_music(final_music, final_clip):
    
    clip_duration = final_clip.duration
    start_time = np.random.randint(0, final_music.duration - clip_duration)
    final_music = final_music.subclip(start_time, start_time + clip_duration)


    final_clip = final_clip.set_audio(final_music)
    return final_clip

def generate_text_label(text, is_question, frame):
    
    is_light = np.mean(frame) > 127
    # font_color = is_light and "black" or "white"
    font_color = "white"
    red_color = (255, 0, 0)
    green_color = (0, 255, 0)
    bg_color = is_question and red_color or green_color
    font_type = './assets/fonts/test.ttf'
    text_clip = TextClip(txt=text,
                        size=(0.875 * VIDEO_RESOLUTION_WIDTH, 0.7 * VIDEO_RESOLUTION_HEIGHT),
                        font=font_type,
                        color=font_color,
                        fontsize=50,
                        kerning=-2, 
                        interline=-1, 
                        method='caption')
    text_clip.margin(top=700)
    text_clip = text_clip.set_position('bottom')
    
    text_clip = text_clip.margin(bottom=MARGIN_TOP, opacity=0)
    # text_clip = text_clip.on_color(size=(text_clip.w+1,text_clip.h+1), color=(0,0,0), pos=('center','center'), col_opacity=0.4)
    
    # if (IS_TEST):
    #     preview = CompositeVideoClip([frame, clip_to_overlay])
    #     preview.save_frame("out.png")
    return text_clip

def add_text(final_clip):

    # print("Adding text to the video number " + str(fact_index) + "), Fact question: " + facts[fact_index]["question"]) 
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

    
    things_to_write = "👉 Haaland breaks the club record for most goals scored in a single season. It's MARCH."
    things_to_write+= "\n\n"
    things_to_write += "👉 Erling Haaland scored 5 goals against RB Leipzig in 57 minutes. It took Lionel Messi 84 minutes & Luiz Adriano 82 minutes to score 5 goals against Bayer Leverkusen & BATE Borisov respectively."
    frame = final_clip.get_frame(0)
    txt_clip2 = generate_text_label(things_to_write, True,frame)
    txt_clip2 = txt_clip2.set_duration(TOTAL_LENGTH_BEFORE_OUTRO)
    final_clip = CompositeVideoClip([final_clip, txt_clip2]) 





    
    final_clip = CompositeVideoClip([final_clip, txt_clip]) 

    return final_clip

def add_image(final_clip):

    # Load the image file
    image = ImageClip("assets/pics/haaland.jpg")

    # Set the dimensions of the image to 9:16
    width, height = image.size
    if width/height > 9/16:
        # Crop the sides of the image
        new_width = int(height * 9/16)
        image = image.crop(x1=(width-new_width)//2, x2=width-(width-new_width)//2)
    else:
        # Crop the top and bottom of the image
        new_height = int(width * 16/9)
        image = image.crop(y1=(height-new_height)//2, y2=height-(height-new_height)//2)
        
        
        # Define the new height
    new_height = 350

    # Calculate the new width to preserve aspect ratio
    width, height = image.size
    new_width = int(new_height * (width / height))

    # Resize the image
    image = image.resize((new_width, new_height))
    image = image.set_pos(('center','top'))
    image.margin(top=350)
    image = image.set_duration(TOTAL_LENGTH_BEFORE_OUTRO)

    # Combine the video and image
    final = CompositeVideoClip([final_clip, image])
    return final


# MAIN CODE ------------------------------------------------


IS_TEST = False
TOTAL_LENGTH_BEFORE_OUTRO = 2 
ADD_OUTRO = False
ADD_MUSIC = False
ADD_TEXT = True
ADD_IMAGE = True

# generate_text_label("test", True)
# TODO reactivate this:
video_dir = IS_TEST and './assets/videos2' or './assets/videos'
print("Generating videos from all videos in the folder " + video_dir)
print(f"Video settings: {TOTAL_LENGTH_BEFORE_OUTRO}s main + {OUTRO_DURATION if ADD_OUTRO else 0}s outro")
final_clip = get_final_clip_from_videos(video_dir)
print(f"Generated base video clip of {final_clip.duration:.1f}s")
print(f"Will generate 1 video of {TOTAL_LENGTH_BEFORE_OUTRO + (OUTRO_DURATION if ADD_OUTRO else 0):.1f}s total length")

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

cur_clip = final_clip.subclip(0, TOTAL_LENGTH_BEFORE_OUTRO)
if (ADD_IMAGE):
    cur_clip = add_image(cur_clip)
if (ADD_TEXT):
    cur_clip = add_text(cur_clip)
if (ADD_OUTRO):
    cur_clip = concatenate_videoclips([cur_clip, OUTRO], method="compose")
    
print("Adding music")
# add the music
if (ADD_MUSIC):
    cur_clip =  add_music(final_music, cur_clip)
    cur_clip = cur_clip.audio_fadeout(OUTRO_DURATION + 1)


max_title_length = 150
video_title_folder = './output/'
video_title_no_ext = 'GlobetrotterChronicles Facts '
# video_title_no_ext += get_facts()[i]["question"] + " "
# if len(video_title_no_ext) < max_title_length:
#     video_title_no_ext += get_hashtag_from_fact(i, max_title_length - len(video_title_no_ext))
video_title = video_title_folder + video_title_no_ext

if not video_title.endswith('.mp4'):
    video_title += '.mp4'

cur_clip.write_videofile(video_title, fps=24, codec='libx264', audio_codec='aac')






