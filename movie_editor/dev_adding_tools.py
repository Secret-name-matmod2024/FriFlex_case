import subprocess
import os

def dict_to_subtitles(jsn):
    pass # subtitles_list_of_dicts

def process_video(input_video, music_file, fragments,  subtitles_list_of_dicts, output_video):
    temp_cropped_videos = []
    for i, (start_time, end_time) in enumerate(fragments):
        temp_cropped_video = f"temp_cropped_video_{i}.mp4"
        crop_video(input_video, start_time, end_time, temp_cropped_video)
        temp_cropped_videos.append(temp_cropped_video)
    merge_videos(temp_cropped_videos, "temp_merged_video.mp4")
    remove_audio("temp_merged_video.mp4", "temp_video_without_audio.mp4")
    add_audio("temp_video_without_audio.mp4", music_file, "processed_video.mp4")
    add_subtitles("processed_video.mp4",  subtitles_list_of_dicts, output_video)
    for temp_file in temp_cropped_videos + ["temp_merged_video.mp4", "temp_video_without_audio.mp4",
                                            "processed_video.mp4"]:
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


fragments = [(10, 20), (40, 60)]
subtitles_list_of_dicts = [{'text':'fhsjdgljfsdklgjdlfs', 'start_t':5, 'end_t':10}, {'text':'AAAAAABBBB', 'start_t':15, 'end_t':20}]
#process_video("video.mp4", "audio.mp3", fragments,  subtitles_list_of_dicts, "processed_video_text.mp4")
add_subtitles('aaaa', subtitles_list_of_dicts, 'vvv')
#todo то же самое для add_text, add_smile

"""ffmpeg.exe -i 20240513_132628.mp4 -vf "movie=20240513_132628.mp4, scale=250:-1[inner];[in][inner]overlay=10:10:enable='between(t,15,20)'[out]" -codec:a copy output.mp4"""