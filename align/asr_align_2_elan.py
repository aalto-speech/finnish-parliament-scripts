#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import sys
from lxml import etree
from datetime import datetime
from mimetypes import guess_type
import fileinput
import time
import os
import codecs
import re
import difflib



def dateIso():
    """ Returns the actual date in the format expected by ELAN. Source:
        http://stackoverflow.com/questions/3401428/how-to-get-an-isoformat-datetime-string-including-the-default-timezone"""
    dtnow = datetime.now()
    dtutcnow = datetime.utcnow()
    delta = dtnow - dtutcnow
    hh, mm = divmod((delta.days * 24 * 60 * 60 + delta.seconds + 30) // 60, 60)
    return '%s%+02d:%02d' % (dtnow.isoformat(), hh, mm)


def parse_asr(rfile):
    """Parses input mseg file"""
    r = []
    for line in rfile:
        line = line.strip()
        start,end,token,alignment_type,speaker_id = line.split("\t",4)
        start_ms = str(int(float(start) * 1000))
        end_ms = str(int(float(end) * 1000))
        new_alignment = start_ms+"\t"+end_ms+"\t"+token+"\t"+alignment_type+"\t"+speaker_id
        r.append(new_alignment)

    #Filter word gaps
    r2 = []
    index = 0
    spoken_segment = ""
    GAP_THRESHOLD = 50
    for line in r:
        start,end,token,alignment_type,speaker_id = line.split("\t",4)
        if index == 0:
            new_alignment = start+"\t"+end+"\t"+token+"\t"+alignment_type+"\t"+speaker_id
            r2.append(new_alignment) 
            prev_start = start
            prev_end = end
            prev_token = token   
        else:
            gap = int(start)-int(prev_end)
            if gap <= GAP_THRESHOLD:
                new_alignment = prev_end+"\t"+end+"\t"+token+"\t"+alignment_type+"\t"+speaker_id
                r2.append(new_alignment)        
                prev_start = start
                prev_end = end
                prev_speaker_id = speaker_id
                prev_token = token  

            else:
                new_alignment = start+"\t"+end+"\t"+token+"\t"+alignment_type+"\t"+speaker_id
                r2.append(new_alignment) 
                prev_start = start
                prev_end = end   
                prev_token = token
        index += 1
    return r2

def write_elan(media_file,rfile, outf):
    """Write Elan file"""
    ts_count = 1
    an_count = 1
    NS = 'http://www.w3.org/2001/XMLSchema-instance'
    location_attr = '{%s}noNamespaceSchemaLocation' % NS
    doc = etree.Element('ANNOTATION_DOCUMENT',
                        attrib={location_attr: 'http://www.mpi.nl/tools/elan/EAFv2.7.xsd',
                                'AUTHOR': '', 'DATE': dateIso(),
                                'FORMAT': '2.7', 'VERSION': '2.7'})
    header = etree.SubElement(doc, 'HEADER',
                              attrib={'MEDIA_FILE': '',
                                      'TIME_UNITS': 'milliseconds'})
    etree.SubElement(header, 'MEDIA_DESCRIPTOR',
                     attrib={'MEDIA_URL': media_file,
                             'MIME_TYPE': guess_type(media_file)[0],
                             'RELATIVE_MEDIA_URL': ''})
    t = etree.SubElement(header, 'PROPERTY',
                         attrib={'NAME': 'lastUsedAnnotationId'})
    t.text = str(len(rfile))
    time = etree.SubElement(doc, 'TIME_ORDER')
    for line in rfile:
        start,end,token,alignment_type,speaker_id = line.split("\t",4)
        etree.SubElement(time, 'TIME_SLOT',
                         attrib={'TIME_SLOT_ID': 'ts' + str(ts_count),
                                 'TIME_VALUE': start})
        ts_count += 1
        etree.SubElement(time, 'TIME_SLOT',
                         attrib={'TIME_SLOT_ID': 'ts' + str(ts_count),
                                 'TIME_VALUE': end})
        ts_count += 1

    #tier = etree.SubElement(doc, 'TIER',attrib={'DEFAULT_LOCALE': 'fi','LINGUISTIC_TYPE_REF': 'default-lt','TIER_ID': 'Speakers'})
    ts_count = 1
    index = 0
    current_speaker = ""
    seg_count = 1
    speakers = []
    for line in rfile:
        start,end,token,alignment_types,speaker_id = line.split("\t",4)
        if speaker_id != current_speaker:
            #speaker_utf8 = speaker_id.decode('iso-8859-15')
            speaker_utf8 = speaker_id
            speaker_utf8 = speaker_utf8.replace(":","")
            tier_id = speaker_utf8.strip()+" "+str(seg_count)
            #tier_id = speaker_utf8.strip()
            speakers.append(speaker_utf8.strip())
            if speaker_utf8.strip() == "Puhuja":
                speaker_utf8 = speakers[len(speakers)-3]
                tier_id = speaker_utf8.strip()+" "+str(seg_count)    
                #tier_id = speaker_utf8.strip()  
            #tier = etree.SubElement(doc, 'TIER',attrib={'DEFAULT_LOCALE': 'fi','LINGUISTIC_TYPE_REF': 'default-lt','TIER_ID': unicode(tier_id),'PARTICIPANT':unicode(speaker_utf8)})
            tier = etree.SubElement(doc, 'TIER',attrib={'DEFAULT_LOCALE': 'fi','LINGUISTIC_TYPE_REF': 'default-lt','TIER_ID': tier_id,'PARTICIPANT':speaker_utf8})
            current_speaker = speaker_id
            seg_count += 1
             		            
        a = etree.SubElement(tier, 'ANNOTATION')
        aa = etree.SubElement(a, 'ALIGNABLE_ANNOTATION',
                         attrib={'ANNOTATION_ID': 'a' + str(an_count),
                                 'TIME_SLOT_REF1': 'ts' + str(ts_count),
                                 'TIME_SLOT_REF2': 'ts' + str(ts_count + 1)})
        #token = token.decode('utf-8')
        av = etree.SubElement(aa,'ANNOTATION_VALUE')
        av.text = token
        an_count += 1
        ts_count += 2
        index += 1

    etree.SubElement(doc, 'LINGUISTIC_TYPE',
                     attrib={'GRAPHIC_REFERENCES': 'false',
                             'LINGUISTIC_TYPE_ID': 'default-lt',
                             'TIME_ALIGNABLE': 'true'})
    etree.SubElement(doc, 'LOCALE',
                     attrib={'COUNTRY_CODE': 'FI',
                             'LANGUAGE_CODE': 'fi'})

    tree = etree.ElementTree(doc)
    tree.write(outf, pretty_print=True,encoding="utf-8")


def first_letter_to_upper(first_word):
    if first_word[0] == "å" or first_word[0] == "ä" or first_word[0] == "ö":
        first_word = first_word[0].replace("å","Å")+first_word[1:]
        first_word = first_word[0].replace("ä","Ä")+first_word[1:]
        first_word = first_word[0].replace("ö","Ö")+first_word[1:]
    else:
        first_word = first_word[0].upper()+first_word[1:]
    return first_word


def time_seg_words(word_1,word_2,s,e):
    start_time = float(s)
    end_time = float(e)
    word_1_len = float(len(word_1))*1.0
    word_2_len = float(len(word_2))*1.0
    duration = end_time - start_time
    dur_word_1 = duration*(word_1_len/(word_1_len+word_2_len))
    dur_word_2 = duration*(word_2_len/(word_1_len+word_2_len))
    start_word_1 = start_time
    end_word_1 = start_time + dur_word_1
    start_word_2 = end_word_1
    end_word_2 = start_word_2+dur_word_2
    return str(start_word_1),str(end_word_1),str(start_word_2),str(end_word_2)

def convert_to_lower(word):
    lower_word = word.lower()
    lower_word = lower_word.replace("Å","å")
    lower_word = lower_word.replace("Ä","ä")
    lower_word = lower_word.replace("Ö","ö")
    return lower_word

def starts_with_lower(word):
    if word[0].islower() == True or word[0:2] == "å" or word[0:2] == "ä" or word[0:2] == "ö":
        return True
    else:
        return False

def align_hyp_ref(reference_snts,hypothesis_snts):
    index = 0
    hypothesis_word_index = 0
    reference_word_index = 0
    alignments = []
    alignment_index = 0
    asr_inserts = []
    INSERT_LIMIT = 4
    for reference_snt in reference_snts:
       hypothesis_snt = hypothesis_snts[index]
       hypothesis_words = []
       hyps = hypothesis_snt.split(" ")   
       for h in hyps:
           h = h.strip()
           if len(h) > 0:
               #h_lower = convert_to_lower(h)
               hypothesis_words.append(h)
       reference_words = []  
       refs = reference_snt.split(" ")
       for r in refs:
           r = r.strip()
           if len(r) > 0:
               #r_lower = convert_to_lower(r)
               reference_words.append(r)
       #Check if hyp and ref are equal length
       if len(hypothesis_words) > len(reference_words):
           sys.stderr.write("More hyp words than refs\n")
           len_diff = len(hypothesis_words) - len(reference_words)
           for i in range(len_diff):
               reference_words.append("*")
       elif len(hypothesis_words) < len(reference_words):
           sys.stderr.write("More ref words than hyps\n")
           len_diff = len(reference_words) - len(hypothesis_words)
           for i in range(len_diff):
               hypothesis_words.append("*")
    
       word_index = 0
       for reference_word in reference_words:
           hypothesis_word = hypothesis_words[word_index]
           if "*" not in reference_word and "*" not in hypothesis_word:
               #Empty insert list first
               if len(asr_inserts) > INSERT_LIMIT:
                   #Segment ASR insert with punctuations
                   for asr_insert in asr_inserts:
                       start,end,hypothesis_time_word = asr_insert.split("\t")
                       alignments.append(start.strip()+"\t"+end.strip()+"\t"+hypothesis_time_word+"\tASR")
                       alignment_index += 1
                   asr_inserts = []
               else:
                   asr_inserts = []
               ########################

               start,end,hypothesis_time_word = hyp_time_words[hypothesis_word_index].split("\t")
               original_reference_word = original_ref_words[reference_word_index]
               if convert_to_lower(hypothesis_time_word) != convert_to_lower(hypothesis_word):
                   alignments.append(start.strip()+"\t"+end.strip()+"\t"+original_reference_word+"\tREF")
                   alignment_index += 1
                   hypothesis_word_index += 1
                   reference_word_index += 1
               else:
                   alignments.append(start.strip()+"\t"+end.strip()+"\t"+original_reference_word+"\tREF")
                   alignment_index += 1
                   hypothesis_word_index += 1
                   reference_word_index += 1
           elif "*" in reference_word and "*" in hypothesis_word:
               pass
           elif "*" in reference_word:
               start,end,hypothesis_time_word = hyp_time_words[hypothesis_word_index].split("\t")
               asr_inserts.append(start.strip()+"\t"+end.strip()+"\t"+hypothesis_time_word)
               hypothesis_word_index += 1
           elif "*" in hypothesis_word:
               #Empty insert list first
               if len(asr_inserts) > INSERT_LIMIT:
                   #Segment ASR insert with punctuations
                   for asr_insert in asr_inserts:
                       start,end,hypothesis_time_word = asr_insert.split("\t")
                       alignments.append(start.strip()+"\t"+end.strip()+"\t"+hypothesis_time_word+"\tASR")
                       alignment_index += 1
                   asr_inserts = []
               else:
                   asr_inserts = []
               ########################

               start,end,hypothesis_time_word = hyp_time_words[hypothesis_word_index-1].split("\t")
               original_reference_word = original_ref_words[reference_word_index]
               if alignment_index != 0:
                   prev_start,prev_end,prev_word,prev_source = alignments[alignment_index-1].split("\t")
                   start_prev_word,end_prev_word,start_reference_word,end_reference_word = time_seg_words(prev_word,reference_word,prev_start,prev_end) 
                   alignments[alignment_index-1] = start_prev_word+"\t"+end_prev_word+"\t"+prev_word+"\t"+prev_source
                   alignments.append(start_reference_word.strip()+"\t"+end_reference_word.strip()+"\t"+original_reference_word+"\tREF")
                   alignment_index += 1
               reference_word_index += 1
           word_index += 1
       index += 1
    return alignments,hypothesis_word_index 



def split_and_realign(ref_filename,hyp_filename):
    ref_file = open(ref_filename,"r",encoding='iso-8859-15')
    ref_line = ref_file.readline()
    ref_file.close()
    hyp_file = open(hyp_filename,"r",encoding='iso-8859-15')
    hyp_line = hyp_file.readline()
    hyp_file.close()
    
    ref,ref_id = ref_line.split("(",1)
    ref = ref.strip()
    hyp,hyp_id = hyp_line.split("(",1)
    hyp = hyp.strip()
    refs = ref.split(" ")
    hyps = hyp.split(" ")
    
    ref_words = []
    for t in refs:
        t = t.strip()
        if len(t) > 0:
            ref_words.append(t)
    hyp_words = []
    for h in hyps:
        h = h.strip()
        if len(h) > 0:
            hyp_words.append(h)
    
    half_way_ref = int(len(ref_words)/2) 
    #New type of alignment
    ref_split_text_1 = ""
    ref_split_text_1_len = 0
    for r in ref_words[0:half_way_ref]:
        ref_split_text_1 += r.strip()+" "
        ref_split_text_1_len += 1
    ref_split_text_1 = ref_split_text_1.strip()
    ref_split_filename = ref_filename+".split"
    ref_split_file = open(ref_split_filename,"w",encoding='iso-8859-15')
    ref_split_file.write(ref_split_text_1+" (session_1)\n")
    ref_split_file.close()
   
    hyp_split_text_1 = ""
    hyp_split_text_1_len = 0
    for h in hyp_words[0:half_way_ref]:
        hyp_split_text_1 += h.strip()+" "
        hyp_split_text_1_len += 1
    hyp_split_text_1 = hyp_split_text_1.strip()
    hyp_split_filename = hyp_filename+".split"
    hyp_split_file = open(hyp_split_filename,"w",encoding='iso-8859-15')
    hyp_split_file.write(hyp_split_text_1+" (session_1)\n")
    hyp_split_file.close()
    session_split_filename = hyp_split_filename+".snt.session"
    os.system("sclite -r "+ref_split_filename+" -h "+hyp_split_filename+" -i rm -o pra stdout > "+session_split_filename)

    ref_snts = []
    hyp_snts = []
    session_file = open(session_split_filename,"r",encoding='iso-8859-15')
    for line in session_file:
        if line.startswith("REF:") or line.startswith(">> REF:"):
            tag,snt = line.split("REF:")
            ref_snts.append(snt.strip())
        elif line.startswith("HYP:") or line.startswith(">> HYP:"):
            tag,snt = line.split("HYP:")
            hyp_snts.append(snt.strip())
    session_file.close()

    index = 0  
    hyp_snt_words = []
    ref_snt_words = []
    hyp_temp_snt_words = []
    ref_temp_snt_words = []  
    for ref_snt in ref_snts:
       hyp_temp_snt_words = []
       ref_temp_snt_words = []  
       hyp_snt = hyp_snts[index]
       hyps = hyp_snt.split(" ")
       for h in hyps:
           h = h.strip()
           if len(h) > 0:
               hyp_snt_words.append(h)
               hyp_temp_snt_words.append(h)
       refs = ref_snt.split(" ")
       for r in refs:
           r = r.strip()
           if len(r) > 0:
               ref_snt_words.append(r)
               ref_temp_snt_words.append(r)

       if len(hyp_temp_snt_words) > len(ref_temp_snt_words):
           len_diff = len(hyp_temp_snt_words) - len(ref_temp_snt_words)
           for i in range(len_diff):
               ref_snt_words.append("*")
       elif len(hyp_temp_snt_words) < len(ref_temp_snt_words):
           len_diff = len(ref_temp_snt_words) - len(hyp_temp_snt_words)
           for i in range(len_diff):
               hyp_snt_words.append("*")
       index += 1

    word_index = 0
    correct_sequence_count = 0
    ref_snt_words.reverse()
    hyp_snt_words.reverse()
    ref_word_index = 0
    hyp_word_index = 0 
    COUNT_THRESHOLD = 4 
    for ref_word in ref_snt_words:
        hyp_word = hyp_snt_words[word_index]
        if "*" not in ref_word and "*" not in hyp_word:
            hyp_word_index += 1
            ref_word_index += 1     
            if starts_with_lower(ref_word) == True and starts_with_lower(hyp_word) == True:
                correct_sequence_count += 1    
            else:
                correct_sequence_count = 0
        elif "*" in ref_word:
            hyp_word_index += 1
            correct_sequence_count = 0
        elif "*" in hyp_word:
            ref_word_index += 1
            correct_sequence_count = 0
        word_index += 1
        if correct_sequence_count >= COUNT_THRESHOLD:
            break   
    split_ref_reverse_index = ref_split_text_1_len - ref_word_index + COUNT_THRESHOLD - 2
    split_hyp_reverse_index = hyp_split_text_1_len - hyp_word_index + COUNT_THRESHOLD - 2

    ref_snt_1 = ""
    ref_snt_2 = ""
    split_ref_index = split_ref_reverse_index   
    for r in ref_words[0:split_ref_index+1]:
        ref_snt_1 += r.strip()+" "
    ref_snt_1 = ref_snt_1.strip()
    
    for r in ref_words[split_ref_index+1:]:
        ref_snt_2 += r.strip()+" "
    ref_snt_2 = ref_snt_2.strip()
    
    ref_snt_1_filename = ref_filename+".1"
    ref_snt_1_file = open(ref_snt_1_filename,"w",encoding='iso-8859-15')
    ref_snt_1_file.write(ref_snt_1+" ("+ref_id.strip()+"\n")
    ref_snt_1_file.close()
    
    ref_snt_2_filename = ref_filename+".2"
    ref_snt_2_file = open(ref_snt_2_filename,"w",encoding='iso-8859-15')
    ref_snt_2_file.write(ref_snt_2+" ("+ref_id.strip()+"\n")
    ref_snt_2_file.close()
    
    hyp_snt_1 = ""
    hyp_snt_2 = ""
    split_hyp_index = split_hyp_reverse_index  
    for h in hyp_words[0:split_hyp_index+1]:
        hyp_snt_1 += h.strip()+" "
    hyp_snt_1 = hyp_snt_1.strip()
    
    for h in hyp_words[split_hyp_index+1:]:
        hyp_snt_2 += h.strip()+" "
    hyp_snt_2 = hyp_snt_2.strip()
    
    hyp_snt_1_filename = hyp_filename+".1"
    hyp_snt_1_file = open(hyp_snt_1_filename,"w",encoding='iso-8859-15')
    hyp_snt_1_file.write(hyp_snt_1+" ("+hyp_id.strip()+"\n")
    hyp_snt_1_file.close()

    hyp_snt_2_filename = hyp_filename+".2"
    hyp_snt_2_file = open(hyp_snt_2_filename,"w",encoding='iso-8859-15')
    hyp_snt_2_file.write(hyp_snt_2+" ("+hyp_id.strip()+"\n")
    hyp_snt_2_file.close()

    #Sclite again
    try:
        sys.stderr.write("Aligning a second time\n")
        session_analysis_filename_1 = hyp_snt_1_filename+".snt.session"
        os.system("sclite -r "+ref_snt_1_filename+" -h "+hyp_snt_1_filename+" -i rm -o pra stdout > "+session_analysis_filename_1)
        session_analysis_filename_2 = hyp_snt_2_filename+".snt.session"
        os.system("sclite -r "+ref_snt_2_filename+" -h "+hyp_snt_2_filename+" -i rm -o pra stdout > "+session_analysis_filename_2)
        sys.stderr.write("Successful this time\n")
    except:
        sys.stderr.write("Failed again, try again\n")
        pass

    ref_snts = []
    hyp_snts = []
    session_analysis_file_1 = open(session_analysis_filename_1,"r",encoding='iso-8859-15')
    for line in session_analysis_file_1:
        if line.startswith("REF:") or line.startswith(">> REF:"):
            tag,snt = line.split("REF:")
            ref_snts.append(snt.strip())
        elif line.startswith("HYP:") or line.startswith(">> HYP:"):
            tag,snt = line.split("HYP:")
            hyp_snts.append(snt.strip())
    session_analysis_file_1.close()
    session_analysis_file_2 = open(session_analysis_filename_2,"r",encoding='iso-8859-15')
    for line in session_analysis_file_2:
        if line.startswith("REF:") or line.startswith(">> REF:"):
            tag,snt = line.split("REF:")
            ref_snts.append(snt.strip())
        elif line.startswith("HYP:") or line.startswith(">> HYP:"):
            tag,snt = line.split("HYP:")
            hyp_snts.append(snt.strip())
    session_analysis_file_2.close()

    #Check if alignment was unsuccessful
    #Call again
    if len(ref_snts) <= 2 and len(hyp_snts) <= 2:
        sys.stderr.write("Recursive alignment\n")
        ref_snts_1,hyp_snts_1 = split_and_realign(ref_snt_1_filename,hyp_snt_1_filename)
        ref_snts_2,hyp_snts_2 = split_and_realign(ref_snt_2_filename,hyp_snt_2_filename)
        ref_snts = ref_snts_1+ref_snts_2
        hyp_snts = hyp_snts_1+hyp_snts_2
    
    #Remove alignment files
    
    os.system("rm "+ref_snt_1_filename)
    os.system("rm "+hyp_snt_1_filename)
    os.system("rm "+ref_snt_2_filename)
    os.system("rm "+hyp_snt_2_filename)
    os.system("rm "+session_analysis_filename_1)
    os.system("rm "+session_analysis_filename_2)
    os.system("rm "+ref_split_filename)
    os.system("rm "+hyp_split_filename)
    os.system("rm "+session_split_filename)
    return ref_snts,hyp_snts

def align_spks_to_snts(asr_aligns,snt_speakers):
    index = 0
    aligned_snts = []
    aligned_snt_string = ""
    current_speaker = "UNKNOWN"
    trn_index = 0
    snt_time_alignments = []
    speaker_sentence_alignments = []
    ASR_INSERT_FLAG = True
    for alignment in asr_aligns:
        start,end,word,source = alignment.split("\t")
        word = word.strip()
        source = source.strip()
        ####################################################################
        try: 
            prev_line = alignments[index-1]
            prev_start,prev_end,prev_word,prev_source = prev_line.split("\t")
        except:
            prev_start = start
            prev_end = end
            prev_word = word
        if prev_word.strip() == "." and index != 0:
            upper_word = first_letter_to_upper(word)
            word = upper_word
    

        if word == ".":
            if index != 0:
                snt_time_alignments.append(start+"\t"+end+"\t"+word+"\t"+source)
                aligned_snt = aligned_snt_string.strip()
                aligned_snts.append(aligned_snt)
                aligned_snt_string = ""
                if ASR_INSERT_FLAG == False and trn_index <= (len(snt_speakers)-1):
                    if current_speaker != snt_speakers[trn_index]:
                        current_speaker = snt_speakers[trn_index]
                    trn_index += 1
                for snt in snt_time_alignments:
                    alignment_out = snt+"\t"+current_speaker.strip()
                    speaker_sentence_alignments.append(alignment_out)
                snt_time_alignments = []

            if source == "REF":
                ASR_INSERT_FLAG = False
            else:
                ASR_INSERT_FLAG = True
        else:
            snt_time_alignments.append(start+"\t"+end+"\t"+word+"\t"+source)    
            aligned_snt_string += word+" " 
        index += 1
    return speaker_sentence_alignments    

    
asr_filename = sys.argv[1].strip()
transcript_filename = sys.argv[2].strip()
metadata_filename = sys.argv[3].strip()
elan_file = sys.argv[4].strip()

#Read media url from metadata file
media_url = ""
metadata_file = open(metadata_filename,'r',encoding='iso-8859-15')
meta_lines = metadata_file.readlines()
for line in meta_lines:
    if line.startswith("Video:"):
        rest,url = line.split(":",1)
        media_url = url.strip()
metadata_file.close()

#Convert time-aligned ASR output to sclite hypothesis format
asr_file = open(asr_filename,"r",encoding='iso-8859-15')
asr_lines_unfiltered = asr_file.readlines()
asr_file.close()

asr_lines = []
prev_word = ""
for line in asr_lines_unfiltered:
    line = line.strip()
    start,end,word = line.split("\t",2)
    if word == "." and prev_word == ".":
        pass
    else:
        asr_lines.append(line)
    prev_word = word

output = ""
hyp_time_words = []
for line in asr_lines:
    start,end,word = line.split("\t")
    hyp_time_words.append(line.strip())
    word = word.strip()
    output += word+" "
file_id,ext = asr_filename.rsplit(".",1)

temp_asr_sclite_filename = file_id+"_"+str(time.time())+".asr"
temp_asr_sclite_file = open(temp_asr_sclite_filename,"w",encoding='iso-8859-15')

temp_asr_sclite_file.write(output+" ("+file_id.strip()+")\n")
temp_asr_sclite_file.close()

#Convert meeting transcript to sclite reference format
output = ""
parenthesis_flag = False
transcript_file = open(transcript_filename,"r",encoding='iso-8859-15')
transcript_lines = transcript_file.readlines()
transcript_file.close()

for line in transcript_lines:
    if line.startswith("PMPVUORO") or line.startswith("KESKUST") or line.startswith("EDPVUORO") or line.startswith("KYSKESK") or line.startswith("ASIAKOHTA"):
        pass
    elif line.startswith("SPEAKER:"):
        if len(output) > 0:
            if output[len(output)-1] == "\n":
                output += line
            else:
                output += "\n"+line
        else:
            output += line
    else:
        words = line.split(" ")
        for word in words:
            if "(" in word:
               parenthesis_flag = True
            word = word.strip()
            match1 = re.search(r'\d\.\d\.\d',word)
            match2 = re.search(r'\d\.\d',word)
            if match1 != None or match2 != None:
                output += word+" "                
            else:
                if (word.endswith("!") or word.endswith(".") or word.endswith("?") or word.endswith(":")) and parenthesis_flag == False:
                    word = word.replace("...",".")
                    word = word.replace("..",".")  
                    word = word.replace("!","!\n")
                    word = word.replace("?","?\n")
                    word = word.replace(".",".\n")
                    if word.endswith(":"):
                        word = word.replace(":",":\n")
                    if len(word) > 0:
                        output += word
                elif word.endswith(".\"") and parenthesis_flag == False:
                    word = word.replace(".\"",".\"\n")
                    if len(word) > 0:
                        output += word
                elif (("!" in word) or ("." in word) or ("?" in word) or (":" in word)) and parenthesis_flag == False:
                    word = word.replace("...",".")
                    word = word.replace("..",".")  
                    word = word.replace("!","!\n")
                    word = word.replace("?","?\n")
                    word = word.replace(".",".\n")
                    if word.endswith(":"):
                        word = word.replace(":",":\n")
                    if len(word) > 0:
                        output += word+" "                   
                else:
                    if len(word) > 0:
                        output += word+" "
            if ")" in word:
               parenthesis_flag = False
                    
lines = output.split("\n")
parenthesis_flag = False

trn_snts = []
trn_snt_speakers = []
current_speaker = "UNKNOWN"

temp_filename = file_id+"_"+str(time.time())+".temp"
temp_out = open(temp_filename,"w",encoding='iso-8859-15')
for line in lines:
    temp_out.write(line.strip()+"\n")
temp_out.close()

temp_filename_preprocessed = temp_filename+".preprocessed"
script_dir = os.path.realpath(__file__).replace("asr_align_2_elan.py","")
os.system(script_dir+"preprocess-parliament.pl "+temp_filename+" > "+temp_filename_preprocessed)
temp_file_processed = open(temp_filename_preprocessed,"r",encoding='iso-8859-15')
temp_processed_lines = temp_file_processed.readlines()
temp_file_processed.close()
for line in temp_processed_lines:
    if "SPEAKER" in line:
        ext,speaker_id = line.split("SPEAKER:",1)
        current_speaker = speaker_id
    else:
        trn_snts.append(line.strip())
        trn_snt_speakers.append(current_speaker)

index = 0
output = ""
for line in trn_snts:
    line = line.strip()
    if index == 0:
        output += ". "+line+" . "
    else:
        output += line+" . "
    index += 1

ref_words = output.split(" ")
original_ref_words = []
for r in ref_words:
    r = r.strip()
    if len(r) > 0:
        original_ref_words.append(r)


temp_transcript_sclite_filename = file_id+"_"+str(time.time())+".transcript"
temp_transcript_sclite_file = open(temp_transcript_sclite_filename,"w",encoding='iso-8859-15')

temp_transcript_sclite_file.write(output.strip()+" ("+file_id.strip()+")\n")
temp_transcript_sclite_file.close()
#Do sclite alignment between ASR output and reference transcript
#Assume sctk module is loaded
session_analysis_filename = temp_asr_sclite_filename+".snt.session"
try:
    os.system("sclite -r "+temp_transcript_sclite_filename+" -h "+temp_asr_sclite_filename+" -i rm -o pra stdout > "+session_analysis_filename)
except:
    sys.stderr.write("First alignment unsuccessful\n")

os.system("iconv -f iso-8859-15 -t utf-8 "+session_analysis_filename+" > "+session_analysis_filename+".new")
os.system("mv "+session_analysis_filename+".new "+session_analysis_filename)
os.system("rm "+temp_filename)
os.system("rm "+temp_filename_preprocessed)


ref_snts = []
hyp_snts = []
session_analysis_file = open(session_analysis_filename,"r",encoding='utf-8')
session_analysis_lines = session_analysis_file.readlines()
session_analysis_file.close()
for line in session_analysis_lines:
    if line.startswith("REF:") or line.startswith(">> REF:"):
        tag,snt = line.split("REF:")
        ref_snts.append(snt.strip())
    elif line.startswith("HYP:") or line.startswith(">> HYP:"):
        tag,snt = line.split("HYP:")
        hyp_snts.append(snt.strip())

asr_alignments,hyp_word_index = align_hyp_ref(ref_snts,hyp_snts)
#Check if aligned correctly
SPLIT_FLAG = False

if hyp_word_index != len(hyp_time_words):
    SPLIT_FLAG = True
    ref_snts,hyp_snts =split_and_realign(temp_transcript_sclite_filename,temp_asr_sclite_filename)
    asr_alignments,hyp_word_index = align_hyp_ref(ref_snts,hyp_snts)
    
    
#Align sentences to speakers
asr_speaker_alignments = align_spks_to_snts(asr_alignments,trn_snt_speakers)

#Convert time stamps to milliseconds
asr_millisecond_alignments = parse_asr(asr_speaker_alignments)

#Write to ELAN format
write_elan(media_url,asr_millisecond_alignments,elan_file)

#Remove temp files
os.system("rm "+session_analysis_filename)
os.system("rm "+temp_transcript_sclite_filename)
os.system("rm "+temp_asr_sclite_filename)





