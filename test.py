import os
import math
import random
import shutil
import audiosegment
from tqdm import tqdm

def create_transcription_line(string):
    # Split the section by line breaks
    lines = string.strip().split('\n')

    if len(lines) < 2:
        return None

    id = lines[0].split(' = ')[1].strip()
    sentence = lines[1].split(' = ')[1].strip()
    start_time = lines[2].split("\t")[10]
    end_time = lines[2].split("\t")[11]

    transcription = {
        'id': id,
        'sentence': sentence,
        'start_time': int(float(start_time) * 1000),
        'end_time': int(float(end_time) * 1000)
    }

    return transcription


def create_transcriptions(orfeo_string):
    # Split the string by sections
    orfeo_split = orfeo_string.split("\n\n")
    transcriptions = []

    for section in orfeo_split:
        transcription = create_transcription_line(section)

        if transcription:
            transcriptions.append(transcription)

    return transcriptions

def create_transcription_string(transcription):
    return f"<s>{transcription['sentence']}</s> {transcription['id']}.16le\n"

def create_transscription_file(transcriptions, filename):
    with open(filename, "w") as f:
        for transcription in transcriptions:
            print(transcription)
            f.write(create_transcription_string(transcription))

def create_audio_files(transcriptions, audio_file, output_folder):
    for transcription in transcriptions:
        start_time = transcription['start_time']
        end_time = transcription['end_time']
        id = transcription['id']

        # Extract the audio
        sample = audiosegment.from_file(audio_file)
        fragment = sample[start_time:end_time]
        fragment.export(output_folder + id + ".16le", format="s16le", bitrate='16k')

if __name__ == "__main__":
    orfeo_string = ""

    f = open("./corpus_fr/01_OG_NH_100222.orfeo", "r")
    orfeo_string = f.read()
    f.close()

    transcriptions = create_transcriptions(orfeo_string)
    print((transcriptions))

    create_transscription_file(transcriptions, "test.txt")

    # create_audio_files(transcriptions, "./corpus_fr/01_OG_NH_100222.wav", "./test_audio_output/")

