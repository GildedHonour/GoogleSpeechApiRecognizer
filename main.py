# -*- coding: utf-8 -*-

import sys
import requests 
from requests.adapters import HTTPAdapter
import json

URL = "https://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium&lang=en-US&maxresults=1"
CHUNK_SIZE_TO_READ = 1024*300
HTTP_STATUS_OK = 200
JSON_STATUS_OK = "5"

if __name__ == "__main__":
  if len(sys.argv) != 2 or "--help" in sys.argv:
    print "Usage: <flac-audio-file>"
    sys.exit(-1)
  else:
    session = requests.Session()
    session.mount('https://', HTTPAdapter(max_retries=5))
    file_name = sys.argv[1]
    rate = 16000 #TODO
    try:
      with open(file_name, "r") as f:
        while True:
          chunk = f.read(CHUNK_SIZE_TO_READ)
          if not chunk:
            break

          while True:
            r = session.post(URL, data=chunk, headers={"Content-Type": "audio/x-flac; rate={0}".format(rate), 
                                      "Content-Length": str(len(chunk))})
            print "status == HTTP_STATUS_OK ? :", r.status_code == HTTP_STATUS_OK
            if r.status_code == HTTP_STATUS_OK:
              print "status is OK: ", r.status_code, ", breaking"
              break
            else:
              print "status is NOT OK: ", r.status_code, ", one more time"

          print "----response----"
          print "code: ", r.status_code
          print "text: ", r.text
          jsdata = json.loads(r.text)
          if jsdata["status"] == JSON_STATUS_OK:
            print "json: ", jsdata["hyptheses"][0]["utterance"]
          else:
            print "it wasn't recognized"

      print "done!"

    except Exception as e:
      print "Unexpected error:", e


# cd alex@ubuntu:~/Documents/python_projects/google_speech_python_api
# python main.py /home/alex/Documents/python_projects/audio_flac/1.flac > /home/alex/Documents/python_projects/google_speech_python_api/log.txt