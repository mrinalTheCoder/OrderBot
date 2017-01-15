
from gtts import gTTS


import argparse
import base64
import json

from googleapiclient import discovery
import httplib2
from oauth2client.client import GoogleCredentials


import pyaudio
import wave
import os

FORMAT = pyaudio.paInt16

CHANNELS = 1
RATE = 16000
CHUNK = int(RATE / 10)
RECORD_SECONDS = 5


DISCOVERY_URL = ('https://{api}.googleapis.com/$discovery/rest?'
                 'version={apiVersion}')


__speech_service__ = None


def get_speech_service():
    credentials = GoogleCredentials.get_application_default().create_scoped(
        ['https://www.googleapis.com/auth/cloud-platform'])
    http = httplib2.Http()
    credentials.authorize(http)

    return discovery.build(
    'speech', 'v1beta1', http=http, discoveryServiceUrl=DISCOVERY_URL)

def initialize():
    global __speech_service__
    if __speech_service__ is None:
            __speech_service__ = get_speech_service()


def record_audio(output_file="/tmp/input.raw"):

    # start Recording
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=CHUNK)
    print "recording..."
    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    print "finished recording"

    # stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()
    file = open(output_file, "w")
    file.write(b''.join(frames))
    file.close()

def text_from_speech(speech_file="/tmp/input.raw"):
    """Transcribe the given audio file.

    Args:
        speech_file: the name of the audio file.
    """
    with open(speech_file, 'rb') as speech:
        speech_content = base64.b64encode(speech.read())

    #service = get_speech_service()
    service_request = __speech_service__.speech().syncrecognize(
        body={
            'config': {
                'encoding': 'LINEAR16',  # raw 16-bit signed LE samples
                'sampleRate': 16000,  # 16 khz
                'languageCode': 'en-IN',  # a BCP-47 language tag
            },
            'audio': {
                'content': speech_content.decode('UTF-8')
                }
            })
    json_response = service_request.execute()
    print(json.dumps(json_response))
    response = json.loads(json.dumps(json_response))
    if "results" in response:
        input = response["results"][0]["alternatives"][0]["transcript"]
        return input
    else:
        return ""

def listen():
    record_audio()
    return text_from_speech()


def say(msg):
    tts = gTTS(text=msg, lang="en-US")
    tts.save("/tmp/temp.mp3")
    os.system("afplay /tmp/temp.mp3")
