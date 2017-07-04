#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import fileinput
import re

metadata_list_filename = sys.argv[1].strip()

links = []
for metadata_filename in fileinput.input(metadata_list_filename):
    metadata_filename = metadata_filename.strip()
    trn_filename = metadata_filename.replace(".metadata",".trn")
    file_id = metadata_filename.replace(".metadata","")
    metadata_file = open(metadata_filename,"r")
    for line in metadata_file:
        line = line.strip()
        if line.startswith("Link: "):
            link = line.replace("Link: ","")
        elif line.startswith("Duration: "):
            duration = line.replace("Duration: ","")
    links.append((link,duration,trn_filename))
    metadata_file.close()

links.sort()
current_audio_file = ""
index = 0
for line in links:
    video_link = line[0]
    duration = line[1]
    trn_filename = line[2]
    link_path,video_file = video_link.rsplit("/",1)
    audio_file = video_file.replace(".mp4",".wav")
    if index == 0:
        os.system("wget "+video_link)
        os.system("avconv -i "+video_file+" -vn -f wav -ar 16000 -ac 1 "+audio_file)
        os.remove(video_file)
        seg_audio_file = trn_filename.replace(".trn",".wav")
        os.system("sox "+audio_file+" -t wav -r 16000 -b 16 -e signed-integer -c 1 "+seg_audio_file+" trim "+duration)
        current_audio_file = audio_file
    else:
        if current_audio_file != audio_file:
            os.system("wget "+video_link)
            os.system("avconv -i "+video_file+" -vn -f wav -ar 16000 -ac 1 "+audio_file)
            os.remove(video_file)
            seg_audio_file = trn_filename.replace(".trn",".wav")
            os.system("sox "+audio_file+" -t wav -r 16000 -b 16 -e signed-integer -c 1 "+seg_audio_file+" trim "+duration)
            os.remove(current_audio_file)
            current_audio_file = audio_file 
        else:
            seg_audio_file = trn_filename.replace(".trn",".wav")
            os.system("sox "+audio_file+" -t wav -r 16000 -b 16 -e signed-integer -c 1 "+seg_audio_file+" trim "+duration)       
    index += 1

os.remove(current_audio_file)
