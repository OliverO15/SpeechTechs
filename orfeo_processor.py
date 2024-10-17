import os
import math
import random
import shutil
import audiosegment
from tqdm import tqdm


def create_transcription_line(string) -> dict or None:
    """Takes in a sentence string and returns a dictionary
    with the id, sentence, start time and end time of that sentence.

    Returns None if the string is not a valid sentence string.
    """
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


def create_transcriptions(orfeo_string, source) -> list:
    """Takes in an orfeo file string and extracts transcriptions or sentences from it.

    Returns a list of dictionaries with the id, sentence, start time and end time of each transcription.
    """

    # Split the string by sections
    orfeo_split = orfeo_string.split("\n\n")
    transcriptions = []

    for section in orfeo_split:
        transcription = create_transcription_line(section)

        if transcription:
            transcription['source'] = source
            transcriptions.append(transcription)

    return transcriptions


def create_transcription_string(transcription) -> str:
    """Takes in a transcription dictionary and returns a string in the format:
    <s>TRANSCRIPTION</s> SOURCE/ID.16le
    """
    return f"<s>{transcription['sentence']}</s> {transcription['source']}/{transcription['id']}.16le\n"


def create_transcription_file(transcriptions, filename):
    """Takes in a list of transcriptions and writes them to a file."""
    with open(filename, "w") as f:
        for transcription in transcriptions:
            f.write(create_transcription_string(transcription))


def create_audio_files(transcriptions, audio_file, output_folder):
    """Takes in a list of transcriptions and an audio file and extracts the audio and outputs
    it in the output folder with the id as the filename. The file is saved in 16le format.
    """

    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for transcription in transcriptions:
        start_time = transcription['start_time']
        end_time = transcription['end_time']
        id = transcription['id']

        # Extract the audio
        sample = audiosegment.from_file(audio_file)
        fragment = sample[start_time:end_time]
        fragment.export(output_folder + id + ".16le", format="s16le", bitrate='16k')


def read_corpus_files(folder_path) -> list:
    """Takes in a folder path and returns a list of all the .orfeo files in that folder."""

    files = []

    for file in os.listdir(folder_path):
        if file.endswith(".orfeo"):
            files.append(file)

    return files


if __name__ == "__main__":
    files = read_corpus_files("./corpus_fr/")
    random.shuffle(files)

    num_test_files = math.floor(len(files) * 0.25)

    test_files = files[:num_test_files]
    train_files = files[num_test_files:]

    # Create the test transcriptions and audio files
    test_transcriptions = []
    for file in test_files:
        f = open(f"./corpus_fr/{file}", "r")
        orfeo_string = f.read()
        f.close()

        transcriptions = create_transcriptions(orfeo_string, 'test')
        test_transcriptions.extend(transcriptions)

        # Create audio files
        create_audio_files(transcriptions, f"./corpus_fr/{file.replace('.orfeo', '.wav')}", "./test/")

    # Create the train transcriptions and audio files
    train_transcriptions = []
    for file in train_files:
        f = open(f"./corpus_fr/{file}", "r")
        orfeo_string = f.read()
        f.close()

        transcriptions = create_transcriptions(orfeo_string, 'train')
        train_transcriptions.extend(transcriptions)

        # Create audio files
        create_audio_files(transcriptions, f"./corpus_fr/{file.replace('.orfeo', '.wav')}", "./train/")

    # Write the transcriptions to a file
    all_transcriptions = train_transcriptions + test_transcriptions
    create_transcription_file(all_transcriptions, 'transcriptions.txt')

