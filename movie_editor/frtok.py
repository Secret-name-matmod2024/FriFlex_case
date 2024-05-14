import subprocess
import os

def process_video(input_video, music_file, fragments, input_text, smiley_file, output_video):
    temp_cropped_videos = []
    for i, (start_time, end_time) in enumerate(fragments):
        temp_cropped_video = f"temp_cropped_video_{i}.mp4"
        crop_video(input_video, start_time, end_time, temp_cropped_video)
        temp_cropped_videos.append(temp_cropped_video)
    merge_videos(temp_cropped_videos, "temp_merged_video.mp4")
    remove_audio("temp_merged_video.mp4", "temp_video_without_audio.mp4")
    add_audio("temp_video_without_audio.mp4", music_file, "processed_video.mp4")
    add_text("processed_video.mp4", input_text, "withtext.mp4")
    add_smiley("withtext.mp4", smiley_file, output_video)
    for temp_file in temp_cropped_videos + ["temp_merged_video.mp4", "temp_video_without_audio.mp4", "processed_video.mp4", "withtext.mp4"]:
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
    command = ['ffmpeg', '-i', input_video, '-i', audio_file, '-c:v', 'copy', '-c:a', 'aac', '-strict', 'experimental', '-map', '0:v:0', '-map', '1:a:0', output_video]
    subprocess.run(command)
    
def add_text(input_video, input_text, start_time, end_time, output_video):
    command = ['ffmpeg', '-i', input_video, '-vf', f"drawtext=text='{input_text}':fontcolor=white:fontsize=36:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=main_h-50-text_h:enable='between(t,{start_time},{end_time})'", '-codec:a', 'copy', output_video]
    subprocess.run(command)
    
def add_smiley(input_video, smiley_file, start_time, end_time, output_video):
    command = ['ffmpeg', '-i', input_video, '-i', smiley_file, '-filter_complex', f"[1:v]scale=iw/5:ih/5 [small_smiley]; [0:v][small_smiley]overlay=5:5:enable='between(t,{start_time},{end_time})'", '-codec:a', 'copy', output_video]
    subprocess.run(command)

def add_subtitles(input_video, subtitles_list_of_dicts, output_video):
    input_text = ''
    subtitle_dict = {
        'fontcolor': 'white',
        'fontsize': '24',
        'box': '1',
        'boxcolor': 'black@0.5',
        'x':'(w-text_w)/2',
        'y':'h-text_h'
    }
    for subtitle in subtitles_list_of_dicts:
        for key in subtitle.keys():
            subtitle_dict[key] = subtitle[key]
        #todo вместо формата сделать '{key}=dict[key]
        tmp = 'drawtext='
        for param in subtitle_dict.keys():
            if param == 'text':
                tmp += f"{param}='{subtitle_dict[param]}':"
            elif param == 'start_t' or param == 'end_t':
                pass
            else:
                tmp += f'{param}={subtitle_dict[param]}:'
        tmp += f"enable='between(t,{subtitle_dict['start_t']},{subtitle_dict['end_t']})',"
        input_text += """drawtext=text='{text}':fontcolor={fontcolor}:fontsize={fontsize}:box={box}:boxcolor={boxcolor}:x={x}:y={y}:enable='between(t,{start_t},{end_t})',""".format(**subtitle_dict)
    print(input_text)
    command = ['ffmpeg', '-i', input_video, '-vf', input_text, '-codec:a', 'copy', output_video]
    subprocess.run(command)

fragments = [(10,20), (40,60)]
input_text = "KKKKKKKKKKKKKKK"
smiley_file = "smile.png"
process_video("video.mp4", "audio.mp3", fragments, input_text, smiley_file, "video_all.mp4")
