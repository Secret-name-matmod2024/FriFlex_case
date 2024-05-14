import subprocess
import os


def process_video(input_video, intro_time, music_file, fragments, input_text, smiley_file, output_video):
    temp_cropped_video = f"intro.mp4"
    add_white_background_with_text(input_text, intro_time, temp_cropped_video)
    temp_cropped_videos = []
    temp_cropped_videos.append(temp_cropped_video)
    for i, (start_time, end_time, fragment_text) in enumerate(fragments):
        temp_cropped_video = f"cropped_{i}.mp4"
        crop_video(input_video, start_time, end_time, "cropped.mp4")
        add_text("cropped.mp4", fragment_text, temp_cropped_video)
       # add_smiley("texted.mp4", smiley_file, temp_cropped_video)
        temp_cropped_videos.append(temp_cropped_video)
        os.remove("cropped.mp4")
        #os.remove("texted.mp4")
    merge_videos(temp_cropped_videos, "merge.mp4")
    remove_audio("merge.mp4", "no_audio.mp4")
    add_audio("no_audio.mp4", music_file, output_video)
    for temp_file in temp_cropped_videos + ["merge.mp4", "no_audio.mp4"]:
        os.remove(temp_file)


def crop_video(input_video, start_time, end_time, output_video):
    command = ['ffmpeg', '-i', input_video, '-ss', str(start_time), '-to', str(end_time), '-c', 'copy', output_video]
    subprocess.run(command)


def merge_videos(input_videos, output_video):
    with open("input.txt", "w") as f:
        for video in input_videos:
            f.write(f"file '{video}'\n")
    command = ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', 'input.txt', '-c', 'copy', output_video]
    subprocess.run(command)
    os.remove("input.txt")


def remove_audio(input_video, output_video):
    command = ['ffmpeg', '-i', input_video, '-c:v', 'copy', '-an', output_video]
    subprocess.run(command)


def add_audio(input_video, audio_file, output_video):
    command = ['ffmpeg', '-i', input_video, '-i', audio_file, '-c:v', 'copy', '-c:a', 'aac', '-strict', 'experimental',
               '-map', '0:v:0', '-map', '1:a:0', output_video]
    subprocess.run(command)


# Пример
"""
изменение стандартного положения x
add_design = {'x':'w-text_w'}
"""


def add_text(input_video, input_text, output_video, start_time=None, end_time=None, add_design={}):
    base_design = {
        'fontcolor': 'white',
        'fontsize': '36',
        'box': '1',
        'boxcolor': 'black@0.5',
        'boxborderw': '5',
        'x': '(w-text_w)/2',
        'y': 'main_h-50-text_h'
    }
    for key in add_design.keys():
        base_design[key] = add_design[key]
    design_cmd_params = f"drawtext=text='{input_text}':"
    for param in base_design.keys():
        design_cmd_params += f'{param}={base_design[param]}:'
    if not(start_time is None or end_time is None):
        design_cmd_params += f"enable='between(t,{start_time},{end_time})'"
    command = ['ffmpeg', '-i', input_video, '-vf', design_cmd_params, '-codec:a', 'copy', output_video]
    subprocess.run(command)


def add_smiley(input_video, smiley_file, output_video, overlay='5:5', start_time=None, end_time=None):
    filter_params = f"[1:v]scale=iw/5:ih/5 [small_smiley]; [0:v][small_smiley]overlay={overlay}"
    if not (start_time is None or end_time is None):
        filter_params += f":enable='between(t,{start_time},{end_time})'"
    command = ['ffmpeg', '-i', input_video, '-i', smiley_file, '-filter_complex',
               filter_params,
               '-codec:a', 'copy', output_video]
    subprocess.run(command)


def add_white_background_with_text(input_text, output_duration, output_video):
    command = ['ffmpeg', '-f', 'lavfi', '-i', 'color=c=white:s=1920x1080:d=5', '-vf',
               f"drawtext=text='{input_text}':fontcolor=black:fontsize=72:x=(w-text_w)/2:y=(h-text_h)/2", '-codec:a',
               'copy', output_video]
    subprocess.run(command)


# Пример subtitles_list_of_dicts
'''
subtitles_list_of_dicts = [{'text':'fhsjdgljfsdklgjdlfs', 'start_t':5, 'end_t':10}, {'text':'AAAAAABBBB', 'start_t':15, 'end_t':20}]
'''


def add_subtitles(input_video, subtitles_list_of_dicts, output_video):
    input_text = ''
    subtitle_dict = {
        'fontcolor': 'white',
        'fontsize': '24',
        'box': '1',
        'boxcolor': 'black@0.5',
        'x': '(w-text_w)/2',
        'y': 'h-text_h'
    }
    for subtitle in subtitles_list_of_dicts:
        for key in subtitle.keys():
            subtitle_dict[key] = subtitle[key]
        tmp = 'drawtext='
        for param in subtitle_dict.keys():
            if param == 'text':
                tmp += f"{param}='{subtitle_dict[param]}':"
            elif param == 'start_t' or param == 'end_t':
                pass
            else:
                tmp += f'{param}={subtitle_dict[param]}:'
        tmp += f"enable='between(t,{subtitle_dict['start_t']},{subtitle_dict['end_t']})',"
        input_text += """drawtext=text='{text}':fontcolor={fontcolor}:fontsize={fontsize}:box={box}:boxcolor={boxcolor}:x={x}:y={y}:enable='between(t,{start_t},{end_t})',""".format(
            **subtitle_dict)
    print(input_text)
    command = ['ffmpeg', '-i', input_video, '-vf', input_text, '-codec:a', 'copy', output_video]
    subprocess.run(command)

fragments = [(10, 20, "11111111"), (40, 60, "22222222")]
intro_time = 5
input_text = "KKKKKKKKKKKKKKK"
smiley_file = "smile.png"
process_video("video.mp4", intro_time, "audio.mp3", fragments, input_text, smiley_file, "video_all.mp4")
