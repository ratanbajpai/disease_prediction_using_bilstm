import concurrent
from threading import Semaphore
import os

import torch
import pandas as pd
from pymetamap import MetaMap
from nltk.sentiment import SentimentAnalyzer
from nltk.sentiment.util import *
from datetime import datetime

# Set METAMAP_PATH variable to the folder where Metamap is installed.
METAMAP_PATH = os.environ.get("METAMAP_PATH")

# Data is not stored as part of project because of its restricted use.
DATA_BASE_PATH = "../data/"
NOTES_FILE = 'Project.csv'
DIAG_FILE = 'DIAGNOSES_ICD.csv'
DIAG_DICT_FILE = 'D_ICD_DIAGNOSES.csv'
SYMPTOMS_FILE = "Symptoms.txt"
mm = MetaMap.get_instance(METAMAP_PATH + '/bin/metamap18')
IRRELEVANT_SECTIONS = [
    "SOCIAL HISTORY:",
    "MEDICATION ON ADMISSION:",
    "DISCHARGE DIAGNOSIS:",
    "ADMISSION DATE"
]

timestamp = datetime.now().strftime('%d-%H-%M-%S')
LAST_RECORD_DONE = 2880
record_processed = 0
semaphore_object = Semaphore(1)


def load_data():
    notes_data = pd.read_csv(DATA_BASE_PATH + NOTES_FILE)
    print(notes_data.head())
    diag_codes = pd.read_csv(DATA_BASE_PATH + DIAG_FILE)
    diag_dict = pd.read_csv(DATA_BASE_PATH + DIAG_DICT_FILE)
    return notes_data, diag_codes, diag_dict


def remove_negative_context_words(text):
    tokens = nltk.word_tokenize(text)
    tokens_neg_marked = nltk.sentiment.util.mark_negation(tokens)
    tokens_without_negative_words = [word for word in tokens_neg_marked if not word.endswith("_NEG")]
    return " ".join(tokens_without_negative_words)


def remove_irrelevant_sections(text):
    lines = text.split("\n")
    output_lines = []
    skip = False
    for line in lines:
        line = line.strip()
        # If Skipping lines, look for end of section indicator - new line for now.
        if skip:
            if not line:
                skip = False
                continue
        else:
            for section_name in IRRELEVANT_SECTIONS:
                if line.upper().startswith(section_name):
                    # print(f"Skipping section : {line}")
                    skip = True

            if not skip:
                output_lines.append(line)
    return "\n".join(output_lines)


def extract_symptoms_using_metamap(text):
    symptoms = []
    # print(text)
    try:
        concepts, error = mm.extract_concepts([text])
        # print(f"concepts : {concepts}")
        for concept in concepts:
            if hasattr(concept, "semtypes"):
                if "sosy" in concept.semtypes or "dsyn" in concept.semtypes:
                    # print(f"concept : {concept}")
                    symptoms.append(concept.preferred_name)
        return symptoms
    except Exception as e:
        print(f"Exception occurred {e}")
        return symptoms


def process_notes(text):
    # print(f"Discharge Summary : {text}")
    # Remove non-relevant sections
    filtered_text = remove_irrelevant_sections(text)

    # Remove negative words
    filtered_neg_text = remove_negative_context_words(filtered_text)

    # Identify relevant concepts from text
    symptoms = extract_symptoms_using_metamap(filtered_neg_text)
    return symptoms


def save_to_file(notes_data, symptoms_list):
    with semaphore_object:
        print(f"printing for {symptoms_list}")
        with open(DATA_BASE_PATH + SYMPTOMS_FILE + "-" + timestamp, 'a') as writer:
            for idx, symptoms in enumerate(symptoms_list):
                print(f"notes_data : {notes_data.iloc[idx, 0]}")
                writer.write(str(notes_data.iloc[idx, 0]) + "," + str(notes_data.iloc[idx, 1])
                             + "," + str(notes_data.iloc[idx, 2]) + ",")
                writer.write("|".join(symptoms))
                writer.write("\n")


def process_chunk(notes_data):
    global record_processed
    print(notes_data.shape)
    record_processed += notes_data.shape[0]
    if record_processed <= LAST_RECORD_DONE:
        print(f"Skipping - record processed - {record_processed}")
        return

    print(f"processing record : {record_processed}")
    symptoms_list = []
    number_of_rec = notes_data.shape[0]
    for index in range(number_of_rec):
        symptoms = process_notes(notes_data.iloc[index, 10])
        print(f"Symptoms : {symptoms}")
        symptoms_list.append(symptoms)

    save_to_file(notes_data, symptoms_list)


def main():
    print("Pre-processing starting now!")
    data_iterator = pd.read_csv(DATA_BASE_PATH + NOTES_FILE, chunksize=10)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(process_chunk, data_iterator)


if __name__ == "__main__":
    main()