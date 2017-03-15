#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
import urllib2
from lxml import etree
from dateutil import parser
import requests
from lxml import html
import urllib

target_dir_base = sys.argv[1].strip()

#Download Channels URL
url = "http://vms.api.qbrick.com/rest/v3/GetAllMedia/24B02715?pageIndex=0&pageSize=2000&profile=android"
fp = urllib2.urlopen(url)
doc = etree.parse(fp)
fp.close()

#target_sessions = [u'Syysistuntokausi 2008',u'Kevätistuntokausi 2009',u'Syysistuntokausi 2009',u'Kevätistuntokausi 2010',u'Syysistuntokausi 2010',u'Kevätistuntokausi 2011',u'Syysistuntokausi 2011',u'Kevätistuntokausi 2012',u'Syysistuntokausi 2012',u'Kevätistuntokausi 2013',u'Syysistuntokausi 2013',u'Kevätistuntokausi 2014',u'Syysistuntokausi 2014',u'Kevätistuntokausi 2015',u'Syysistuntokausi 2015',u'Kevätistuntokausi 2016',u'Syysistuntokausi 2016']
target_sessions = [u'Syysistuntokausi 2016']

target_session_ids = []
for target_session in target_sessions:
    for d in doc.xpath(u'//category[contains(@name,"Täysistunnot")]//categories//category[contains(@name,\"'+target_session+'\")]'):
        target_session_ids.append(d.attrib['id'])

parliament_sessions = []
for d in doc.xpath('//media//item'):
    target_flag= False
    video_title = d.xpath('./title//text()')[0]
    video_date  = d.xpath('./publishdate//text()')[0]
    for cat in d.xpath('./categories//category'):
        if cat.text in target_session_ids:
            target_flag = True
    if target_flag:
        for s in d.xpath('./playlist//stream//format//substream'):
            if 'mimetype' in s.attrib:
                video_url =  s.text.encode('utf-8')
                parliament_sessions.append((video_date,video_title,video_url))

election_years = [2007,2011,2015,2019]

modified_file_list = []
modified_flag = False
for session in parliament_sessions:
    session_date = session[0]
    session_title =  session[1]
    session_url = session[2]
    dt = parser.parse(session_date)
    #print session_url
    #Retrieve corresponding meeting transcript
    try:
        transcript_id,rest = session_title.split(". ",1)
        if dt.year >= 2015:
            if dt.year == 2015 and int(transcript_id) >= 135:
                transcript_url = "https://www.eduskunta.fi/FI/Vaski/sivut/trip.aspx?triptype=ValtiopaivaAsiakirjat&docid=ptk+"+transcript_id+"/"+str(dt.year-1)    
                transcript_page = requests.get(transcript_url)
                transcript_tree = html.fromstring(transcript_page.text)
            else:
                transcript_url = "https://www.eduskunta.fi/FI/vaski/poytakirja/Sivut/PTK_"+transcript_id+"+"+str(dt.year)+".aspx"
                transcript_page = requests.get(transcript_url)
                transcript_tree = html.fromstring(transcript_page.text)
        else:
            if (dt.year in election_years) and (dt.month >= 1 and dt.month <=5) and (int(transcript_id) > 100):
                transcript_url = "https://www.eduskunta.fi/FI/Vaski/sivut/trip.aspx?triptype=ValtiopaivaAsiakirjat&docid=ptk+"+transcript_id+"/"+str(dt.year-1)
                transcript_page = requests.get(transcript_url)
                transcript_tree = html.fromstring(transcript_page.text)
            else: 
                transcript_url = "https://www.eduskunta.fi/FI/Vaski/sivut/trip.aspx?triptype=ValtiopaivaAsiakirjat&docid=ptk+"+transcript_id+"/"+str(dt.year)
                transcript_page = requests.get(transcript_url)
                transcript_tree = html.fromstring(transcript_page.text)
        if transcript_url.endswith(".aspx"):
            transcript_sections = transcript_tree.xpath('//div[@class]')
            pmpvuoro_index = 0
            transcript_output = ""
            for ts in transcript_sections:
                if 'class' in ts.attrib:
                    if ts.attrib['class'] == "AsiaKohtaLinkki":
                        transcript_output += "ASIAKOHTA\n"
                        for a in ts:
                            if a.tag == "a":
                                meeting_url = "https://www.eduskunta.fi"+a.attrib['href']
                                meeting_page = requests.get(meeting_url)
                                meeting_tree = html.fromstring(meeting_page.text)
                                talks = meeting_tree.xpath('//div[@class]')
                                index = 0
                                for p in talks:
                                    try:
                                        prev_p = talks[index-1]
                                    except:
                                        prev_p = p
                                    try:
                                        next_p = talks[index+1]
                                    except:
                                        next_p = p
                                    
                                    if 'class' in p.attrib:
                                        if p.attrib['class'] == "Henkilo":
                                            sub_elements = p.xpath('*/div[@class]')
                                            speaker_info = "" 
                                            for element in sub_elements:
                                                if element.attrib['class'] == "LisatietoTeksti":
                                                    speaker_info += "("+element.text_content()+") "                                                
                                                else:
                                                    speaker_info += element.text_content()+" "
                                            speaker_info = speaker_info.strip()
                                            if len(speaker_info) > 0:
                                                speaker_info = "SPEAKER: "+speaker_info
                                                transcript_output += speaker_info.encode('iso-8859-15','ignore')+"\n"
                                        elif p.attrib['class'] == "PuheenjohtajaTeksti":
                                            chairman_name = p.text_content()
                                            transcript_output += "SPEAKER: "+chairman_name.encode('iso-8859-15','ignore')+"\n" 
                                        elif p.attrib['class'] == "KappaleKooste":
                                            text_prompt = p.text_content()
                                            transcript_output += text_prompt.encode('iso-8859-15','ignore')+"\n"
                                    index += 1                                                
        else:
            transcript_sections = transcript_tree.xpath('//div[@class]')
            pmpvuoro_index = 0
            transcript_output = ""
            for ts in transcript_sections:
                if 'class' in ts.attrib:
                    if ts.attrib['class'] == "PMPVUORO":
                        transcript_output += "PMPVUORO\n"
                        talk =  ts.text_content()
                        for p in ts:
                            if p.tag == "p":
                                if 'class' in p.attrib:
                                    if p.attrib['class'] == "inline strong":
                                        speaker = p.text_content()
                                        speaker = speaker.replace("\n"," ")
                                        speaker = speaker.strip()
                                        transcript_output += "SPEAKER: "+speaker.encode('iso-8859-15','ignore')+"\n"
                        talk_lines = talk.split("\n")
                        for talk_line in talk_lines:
                            if talk_line.strip() != speaker.strip():
                                talk_line = talk_line.strip()
                                transcript_output += talk_line.encode('iso-8859-15','ignore')+"\n"
                    elif ts.attrib['class'] == "EDPVUORO":
                        transcript_output += "EDPVUORO\n"
                        talk =  ts.text_content()
                        for p in ts:
                            if p.tag == "p":
                                if 'class' in p.attrib:
                                    if p.attrib['class'] == "strong inline":
                                        speaker = p.text_content()
                                        speaker = speaker.replace("\n"," ")
                                        speaker = speaker.strip()
                                        transcript_output += "SPEAKER: "+speaker.encode('iso-8859-15','ignore')+"\n"
                        talk_lines = talk.split("\n")
                        for talk_line in talk_lines:
                            if talk_line.strip() != speaker.strip():
                                talk_line = talk_line.strip()
                                transcript_output += talk_line.encode('iso-8859-15','ignore')+"\n"
                    elif ts.attrib['class'] == "KESKUST":
                        transcript_output += "KESKUST\n"
                        for p in ts:
                            if p.tag == "p":
                                for a in p:
                                    if a.tag == "a" and 'class' in a.attrib: 
                                        if a.attrib['class'] == "OTSIS":
                                            meeting_url = "https://www.eduskunta.fi"+a.attrib['href']
                                            meeting_page = requests.get(meeting_url)
                                            meeting_tree = html.fromstring(meeting_page.text)
                                            talks = meeting_tree.xpath('//div[@class="PVUORO"]//p')
                                            for p in talks:
                                                if p.tag == "p":
                                                    if 'class' in p.attrib:
                                                        if 'inline' in p.attrib['class']:
                                                            speaker = p.text_content()
                                                            speaker = speaker.replace("\n"," ")
                                                            speaker = speaker.strip()
                                                            transcript_output += "SPEAKER: "+speaker.encode('iso-8859-15','ignore')+"\n"                           
                                                    elif 'xmlns:edk' in p.attrib:
                                                        talk = p.text_content()
                                                        talk_lines = talk.split("\n")
                                                        for talk_line in talk_lines:
                                                            talk_line = talk_line.strip() 
                                                            transcript_output += talk_line.encode('iso-8859-15','ignore')+"\n"                                 
                    elif ts.attrib['class'] == "KYSKESK":
                        modified_flag = True
                        transcript_output += "KYSKESK\n"
                        for a in ts:
                            if a.tag == "a" and 'class' in a.attrib:
                                if a.attrib['class'] == "KYSYM":
                                    meeting_url = "https://www.eduskunta.fi"+a.attrib['href']
                                    meeting_page = requests.get(meeting_url)
                                    meeting_tree = html.fromstring(meeting_page.text)
                                    talks = meeting_tree.xpath('//div[@class="SKTPVUOR"]//*')
                                    for p in talks:
                                        if p.tag == "p":
                                            if 'class' in p.attrib:
                                                 if 'inline' in p.attrib['class']:
                                                     speaker = p.text_content()
                                                     speaker = speaker.replace("\n"," ")
                                                     speaker = speaker.strip()
                                                     transcript_output += "SPEAKER: "+speaker.encode('iso-8859-15','ignore')+"\n"                           
                                            elif 'xmlns:edk' in p.attrib:
                                                 talk = p.text_content()
                                                 talk_lines = talk.split("\n")
                                                 for talk_line in talk_lines:
                                                     talk_line = talk_line.strip() 
                                                     transcript_output += talk_line.encode('iso-8859-15','ignore')+"\n"
                                        elif p.tag == "span":
                                            if 'class' in p.attrib:
                                                if 'inline' in p.attrib['class']:
                                                     speaker = p.text_content()
                                                     speaker = speaker.replace("\n"," ")
                                                     speaker = speaker.strip()
                                                     transcript_output += "SPEAKER: "+speaker.encode('iso-8859-15','ignore')+"\n"
        print "Saving transcripts"
        print len(transcript_output)             
        if len(transcript_output) > 0:
            #target_dir = target_dir_base+"/"+str(dt.year)
            target_dir = target_dir_base
            if os.path.isdir(target_dir) == False:
                os.mkdir(target_dir)
            #Save meeting transcript
            transcript_filename = target_dir+"/"+"session_"+str(transcript_id)+"_"+str(dt.year)+".transcript"
            transcript_file = open(transcript_filename,"w")
            transcript_file.write(transcript_output)
            transcript_file.close()
            #Save video file
            video_filename = target_dir+"/"+"session_"+str(transcript_id)+"_"+str(dt.year)+".mp4"
            urllib.urlretrieve(session_url,video_filename) 
            #Convert to audio
            audio_filename = video_filename.replace(".mp4",".wav")
            os.system("avconv -i "+video_filename+" -vn -f wav -ar 16000 -ac 1 "+audio_filename)
            os.system("rm "+video_filename)
            #Save metadata file       
            metadata_filename = target_dir+"/"+"session_"+str(transcript_id)+"_"+str(dt.year)+".metadata"
            metadata_file = open(metadata_filename,"w")
            protocol,address = session_url.split("://",1)
            if protocol == "http":
                address = address.replace("down0.","down0-",1)
                session_url = "https://"+address
            metadata = "Published: "+session_date.encode('utf-8','ignore')+"\n"
            metadata += "Video: "+session_url.decode('utf-8','ignore')+"\n"
            metadata += "Transcript: "+transcript_url.encode('utf-8','ignore')+"\n"
            metadata_file.write(metadata.encode('iso-8859-15','ignore'))
            metadata_file.close()
        else:
            #target_dir = target_dir_base+"/"+str(dt.year)
            target_dir = target_dir_base
            if os.path.isdir(target_dir) == False:
                os.mkdir(target_dir)
            missing_filename = target_dir+"/missing_transcripts.list"
            missing_file = open(missing_filename,"a")
            protocol,address = session_url.split("://",1)
            if protocol == "http":
                address = address.replace("down0.","down0-",1)
                session_url = "https://"+address

            metadata = "Published: "+session_date.encode('utf-8','ignore')+"\n"
            metadata += "Video: "+session_url.decode('utf-8','ignore')+"\n"
            metadata += "Transcript: "+transcript_url.encode('utf-8','ignore')+"\n"
            missing_file.write(metadata.encode('iso-8859-15','ignore'))
            missing_file.close()  
    except:
        print "Unexpected error:", sys.exc_info()[0]
