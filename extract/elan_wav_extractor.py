#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import fileinput
import re

def replace_chars(match):
    char = match.group(0)
    return chars[char]

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

# remove strange characters
chars = {
    '\xc2\x82' : ',',        # High code comma
    '\xc2\x84' : ',,',       # High code double comma
    '\xc2\x85' : '...',      # Tripple dot
    '\xc2\x88' : '^',        # High carat
    '\xc2\x91' : '\x27',     # Forward single quote
    '\xc2\x92' : '\x27',     # Reverse single quote
    '\xc2\x93' : '\x22',     # Forward double quote
    '\xc2\x94' : '\x22',     # Reverse double quote
    '\xc2\x95' : ' ',
    '\xc2\x96' : '-',        # High hyphen
    '\xc2\x97' : '--',       # Double hyphen
    '\xc2\x99' : ' ',
    '\xc2\xa0' : ' ',
    '\xc2\xa6' : '|',        # Split vertical bar
    '\xc2\xab' : '<<',       # Double less than
    '\xc2\xbb' : '>>',       # Double greater than
    '\xc2\xbc' : '1/4',      # one quarter
    '\xc2\xbd' : '1/2',      # one half
    '\xc2\xbe' : '3/4',      # three quarters
    '\xca\xbf' : '\x27',     # c-single quote
    '\xcc\xa8' : '',         # modifier - under curve
    '\xcc\xb1' : ''          # modifier - under line
}

#First read in ELAN file
sys.stderr.write("Reading ELAN files\n")
elan_list = sys.argv[1].strip()
elan_list_file = open(elan_list,"r")
sentence_segs = []
for elan_filename in elan_list_file:
    elan_filename = elan_filename.strip()
    metadata_filename = elan_filename.replace(".eaf",".metadata")
    metadata_file = open(metadata_filename,"r")
    metadata_line = metadata_file.readline()
    metadata_file.close()
    metadata_line = metadata_line.strip()
    ext,publish_date,ext2 = metadata_line.split(" ",2)
    publish_date = publish_date.strip()
    publish_date = publish_date.replace("-","_")
 
    audio_filename = elan_filename.replace(".eaf",".wav")
    time_slots = dict()
    asr_word_segs = []
    start_ref = "0"
    end_ref = "0"
    current_participant = "Unknown"
    for line in fileinput.input(elan_filename):
        line = line.strip()
        line = re.sub('(' + '|'.join(chars.keys()) + ')', replace_chars, line)
        if line.startswith("<MEDIA_DESCRIPTOR"):
            ext1,media_url,ext2,ext3 = line.split(" ",3)
            media_url = media_url.replace("MEDIA_URL=","")
            media_url = media_url.replace("\"","")
            ext,media_url = media_url.rsplit("/",1)
            file_id,ext = media_url.rsplit(".",1)
        elif line.startswith("<TIER"):
            ext1,ext2 = line.split("PARTICIPANT=",1)
            participant,ext3 = ext2.split("TIER_ID=",1)
            participant = participant.strip()
            participant = participant.replace("\"","")
            current_participant = participant
        elif line.startswith("<TIME_SLOT"):
            line = line.replace("\"","")
            line = line.replace("/>","")
            line = line.replace("<","")
            ext,time_slot_id,time_value = line.split(" ",2)
            time_slot_id = time_slot_id.replace("TIME_SLOT_ID=","")
            time_value = time_value.replace("TIME_VALUE=","")
            time_slots[time_slot_id.strip()] = time_value.strip()
        elif line.startswith("<ALIGNABLE_ANNOTATION"):
            line = line.replace("\"","")
            line = line.replace("<","")
            line = line.replace(">","")
            ext,annotation_id,start_ref,end_ref = line.split(" ",3)
            start_ref = start_ref.replace("TIME_SLOT_REF1=","")
            end_ref = end_ref.replace("TIME_SLOT_REF2=","")
        elif line.startswith("<ANNOTATION_VALUE"):
            word = line.replace("<ANNOTATION_VALUE>","")
            word = word.replace("</ANNOTATION_VALUE>","")
            start_time = str(float(int(time_slots[start_ref])/1000.0))
            end_time = str(float(int(time_slots[end_ref])/1000.0))
            asr_word_segs.append(start_time+"\t"+end_time+"\t"+current_participant+"\t"+word.strip())    
    word_segs_filtered = []
    index = 0
    prev_word = ""
    for line in asr_word_segs:
        start,end,participant,word = line.split("\t")
        try: 
            next_line = word_segs[index+1]
            next_start,next_end,next_participant,next_word = next_line.split("\t")
        except:
            next_start = start.strip()
            next_end = end.strip()
            next_participant = participant.strip()
            next_word = word.strip()
        word = word.strip()
        participant = participant.strip()
    
        if word == ".":
            if prev_word == ".":
                pass
            else:
                word_segs_filtered.append(line) 
        else:
            word_segs_filtered.append(line) 
        prev_word = word    
    index = 0
    sentence = ""
    sentence_start_time = 0.0
    for line in word_segs_filtered:
        start,end,participant,word = line.split("\t")
        word = word.strip()
        if len(sentence) == 0 and index != 0:
            sentence_start_time = start
        try: 
            prev_line = word_segs_filtered[index-1]
            prev_start,prev_end,prev_participant,prev_word = prev_line.split("\t")
        except:
            prev_start = start
            prev_end = end
            prev_participant = participant
            prev_word = word
        try: 
            next_line = word_segs_filtered[index+1]
            next_start,next_end,next_participant,next_word = next_line.split("\t")
        except:
            next_start = start
            next_end = end
            next_participant = participant
            next_word = word
        if word == ".":
            sentence = sentence.strip()
            participant = participant.split("/",1)[0]
            participant = participant.split("(",1)[0]
            if "Puhemies " in participant:
                participant = participant.split("Puhemies",1)[1]
            if "puhemies " in participant:
                participant = participant.split("puhemies",1)[1]
            if "ministeri " in participant:
                participant = participant.split("ministeri",1)[1]
            if "Ministeri " in participant:
                participant = participant.split("Ministeri",1)[1]
            participant = participant.strip()
            participant = " ".join(participant.split())
            sentence_segs.append((participant,float(sentence_start_time),float(prev_end),sentence,audio_filename,publish_date)) 
            sentence_start_time = next_start.strip()
            sentence = ""    
        else:
            sentence += word+" "
        index += 1


elan_list_file.close()
#Extract audio segments and sentences
target_dir = sys.argv[2].strip()
sentence_segs.sort()
speaker_seg_index = 1
speaker_id_index = 0
current_speaker = ""
ph_set = []
align_recipes = []
run_lines = []
for s in sentence_segs:
    speaker = s[0]
    start_s = float(s[1])
    end_s = float(s[2])
    trn = s[3]
    audio_filename = s[4].strip()
    publish_date = s[5].strip()

    speaker = speaker.replace(" ","_")
    speaker = speaker.replace("-","_")
    speaker = speaker.lower()
    speaker = speaker.replace("Å","a")
    speaker = speaker.replace("Ä","a")
    speaker = speaker.replace("Ö","o")
    speaker = speaker.replace("å","a")
    speaker = speaker.replace("ä","a")
    speaker = speaker.replace("ö","o")
    if len(trn) > 2 and ("unknown" not in speaker) and ("puhemies" not in speaker):
        if speaker != current_speaker:
            speaker_seg_index = 1
            current_speaker = speaker
            speaker_id_index += 1
        else:
            speaker_seg_index += 1
            current_speaker = speaker
    
        str_seg_index = '{:05}'.format(speaker_seg_index)
        str_id_index = '{:04}'.format(speaker_id_index)
        #Extract audio segment
        if os.path.isdir(target_dir) == False:
            os.mkdir(target_dir)
        speaker_dir = target_dir+"/"+str_id_index
        if os.path.isdir(speaker_dir) == False:
            os.mkdir(speaker_dir)
        seg_audio_filename = speaker_dir+"/"+current_speaker+"_"+str_seg_index+".wav"
        start_time = float(start_s)
        end_time = float(end_s)
        duration = end_time-start_time
        try:
            os.system("sox "+audio_filename+" -t wav -r 16000 -b 16 -e signed-integer -c 1 "+seg_audio_filename+" trim "+str(start_time)+" "+str(duration))
        except:
            pass
        #write sentence
        seg_trn_filename = seg_audio_filename.replace(".wav",".trn")
        trn = trn.lower()
        trn = trn.replace("Å","å")
        trn = trn.replace("Ä","ä")
        trn = trn.replace("Ö","ö")
        trn = trn.replace("-"," ")
        trn = trn.replace(".","")
        trn = trn.replace("?","")
        trn = trn.replace("!","")
        trn = trn.replace(":","")
        seg_trn_file = open(seg_trn_filename,"w")
        seg_trn_file.write(trn+"\n")
        seg_trn_file.close()
        #Write metadata file
        seg_metadata_filename = seg_audio_filename.replace(".wav",".metadata")
        seg_metadata_file = open(seg_metadata_filename,"w")
        seg_metadata_file.write(publish_date+"\n")
        seg_metadata_file.close()
