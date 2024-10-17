import os
import math
import random
import shutil
import audiosegment
from tqdm import tqdm


A = 0

def get_train_test(filenames: list[str], test_size: float=0.25):
    num_files = len(filenames)
    num_test_files = math.floor(num_files * test_size)
    
    test_files = random.sample(filenames, num_test_files)
    train_files = [file for file in filenames if file not in test_files]
    
    return train_files, test_files


def generate_sentences(filename, corpus_path, dest_dir, transcription_filepath):
    global A
    print("Generating sentences for file", filename)
    
    count = 0
    prev_line = ""
    out_file = open(transcription_filepath, "a")
    
    info = {}
    
    for line in open(os.path.join(corpus_path, f"{filename}.orfeo"), "r"):
        #TODO: consider sentences that have just one word
        if count == 0:
            # First line
            out_filename = line.split(" ")[-1][:-1]
        
        if count == 1:
            text = line[len("# text = "):-1]
        
        if count == 2:
            # This is where the starting time fo the sentence is stored
            start_sec = float(line.split("\t")[-3])
            
        if line == "\n":
            # Last line of the sentence is reached
            count = 0
            
            end_sec = float(prev_line.split("\t")[-2])
            # __generate_sentence(start_sec, end_sec, f"{os.path.join(corpus_path, filename)}.wav", out_filename, dest_dir)
            info[out_filename] = [start_sec, end_sec]
            
            out_file.write(f"<s>{text}</s> {dest_dir}/{out_filename}.wav\n")
        else:
            count += 1
        
        prev_line = line
    
    out_file.close()
    A += len(info)
    # __generate_sentence(info, os.path.join(corpus_path, f"{filename}.wav"), dest_dir)
    
    


# def __generate_sentence(start, end, in_filename, out_filename, dest_dir): 
def __generate_sentence(info, in_filename, dest_dir): 
    sample = audiosegment.from_file(in_filename)
    
    for file, time in tqdm(info.items(), desc=f"Generating sentences..."):
        start = time[0]
        end = time[1]
        fragment = sample[round(start * 1000, 2):round(end * 1000, 2)]
        fragment.export(os.path.join(dest_dir, f"{file}.wav"))

if __name__ == "__main__":
    
    CORPUS_PATH = "corpus_fr"
    random.seed(42) # Set the same random seed so that the results are deterministic

    if not os.path.isdir(CORPUS_PATH):
        print(f"{CORPUS_PATH} is not a valid directory")
        exit(-1)

    # Get unique file names
    filenames = []
    for file in sorted(os.listdir(CORPUS_PATH)):
        name, extension = os.path.splitext(file)
        
        if extension == ".wav":
            filenames.append(name)
    
    print(f"{len(filenames)} files found.")
    
    train, test = get_train_test(filenames)
    
    print(f"{len(train)} training samples.")
    print(f"{len(test)} testing samples.")
    
    
    TRAIN_PATH = os.path.join(CORPUS_PATH, "corpus_fr_train")
    TEST_PATH = os.path.join(CORPUS_PATH, "corpus_fr_test")
    
    
    if os.path.exists(TRAIN_PATH):
        print(f"Training dataset already exists in {TRAIN_PATH}")
    else:
        print(f"Creating training dataset directory")
        os.mkdir(TRAIN_PATH)
    
    if os.path.exists(TEST_PATH):
        print(f"Testing dataset already exists in {TEST_PATH}")
    else:
        print(f"Creating testing dataset directory")
        os.mkdir(TEST_PATH)


    transcription_file = "transcription_file.txt"
    
    for file in train:
        generate_sentences(file, CORPUS_PATH, TRAIN_PATH, transcription_file)
    
    for file in test:
        generate_sentences(file, CORPUS_PATH, TEST_PATH, transcription_file)
    