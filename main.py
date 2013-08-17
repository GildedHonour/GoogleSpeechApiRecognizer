# -*- coding: utf-8 -*-

import sys
import requests 
from requests.adapters import HTTPAdapter
import json
import os
import subprocess
import csv

URL = "https://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium&lang=en-US&maxresults=1"
CHUNK_SIZE_TO_READ = 1024*300
HTTP_STATUS_OK = 200
JSON_STATUS_OK = 0
RESULT_CSV_FILE_NAME = "/home/alex/Documents/python_projects/audio_flac/results.csv"

def get_file_rate(file_name):
  p = subprocess.Popen("soxi %s | grep 'Sample Rate' | awk '{print $4}'" % file_name, 
    shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

  stdout, stderr = p.communicate()
  return stdout

def list_files(dir):
  os.chdir(dir)
  for file_name in os.listdir("."):
    if file_name.endswith(".flac"):
      yield file_name

def save_result_to_csv(file_name, result):
  with open(RESULT_CSV_FILE_NAME,"a+") as f:
    out = csv.writer(f, delimiter=',',quoting=csv.QUOTE_ALL)
    out.writerow([file_name, result])

if __name__ == "__main__":
  if len(sys.argv) != 2 or "--help" in sys.argv:
    print "Usage: <flac-audio-files-path>"
    sys.exit(-1)
  else:
    session = requests.Session()
    session.mount('https://', HTTPAdapter(max_retries=5))
    for file_name in list_files(sys.argv[1]):
      print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`"
      print "---file_name: ", file_name
      rate = get_file_rate(file_name)
      print "---rate: ", rate

      try:
        with open(file_name, "r") as f:
          while True:
            chunk = f.read(CHUNK_SIZE_TO_READ)
            if not chunk:
              break

            while True:
              r = session.post(URL, data=chunk, headers={"Content-Type": "audio/x-flac; rate={0}".format(rate), 
                                        "Content-Length": str(len(chunk))})
              if r.status_code == HTTP_STATUS_OK:
                print "---http status is OK: ", r.status_code, ", breaking"
                break
              else:
                print "---http status is NOT OK: ", r.status_code, ", one more time"

            print "----response----"
            print "---code: ", r.status_code
            print "---text: ", r.text
            jsdata = json.loads(r.text)

            if jsdata["status"] == JSON_STATUS_OK:
              result = jsdata["hypotheses"][0]["utterance"]
              print "---json: ", result
            else:
              result = "---it wasn't recognized"
              print result

            save_result_to_csv(file_name, result)

        print "------------------------------------------------"
        print "done!"

      except Exception as e:
        print "Unexpected error:", e


# cd ~/Documents/python_projects/google_speech_python_api
# python main.py ~/Documents/python_projects/audio_flac/1.flac > log.txt
# python main.py /home/alex/Documents/python_projects/audio_flac > log.txt