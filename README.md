# finnish-parliament-scripts
Scripts for retrieving and aligning speech and meeting transcripts from the web portal of the Parliament of Finland (https://www.eduskunta.fi)

Dependencies:
- sox
- avconv
- sclite
- python3
- python3-lxml

Download videos and meeting transcripts and save into DATA-FOLDER:
-------------------------
```bash
retrieve/retrieve_sessions.py DATA-FOLDER
```

Four different files will be saved for each session:
- *.mp4 - video of the session
- *.wav - audio file stored in wav-format (16kHz,mono)
- *.transcript - meeting transcript with speaker information for each paragraph
- *.metadata - metadata file containing date information and links to the original video and meeting transcript

Produce first-pass recognition output with an ASR system (preferably train a biased LM with the meeting transcripts).
-------------------------
Store recognition output in the following format:
- start-time-in-seconds end-time-in-seconds word

Align the first-pass output with the meeting transcript using sclite:
-------------------------
```bash
align/asr_align_2_elan.py asr-output transcript-file metadata-filename elan-filename
```

The output is in the Elan EAF-format.

Test the alignment script with example files:
```bash
align/asr_align_2_elan.py test/session_79_2008.asr test/session_79_2008.transcript test/session_79_2008.metadata test/session_79_2008.eaf
```

Optionally you can extract individual speech segments from a list of EAF-files:
-------------------------
```bash
extract/elan_wav_extractor.py eaf-list wav-segment-dir
```

Stores both audio file (.wav) and transcript (.trn)

André Mansikkaniemi, andre.mansikkaniemi@aalto.fi
