import pandas as pd


def main(filename):
    # Need to collect HADM_ID from original file
    index_to_hadm = {}
    data_iterator = pd.read_csv("../data/filtered_notes.csv", chunksize=10)
    for chunks in data_iterator:
        num_of_records = chunks.shape[0]
        for index in range(num_of_records):
            if "Discharge summary" in str(chunks.iloc[index, 7]):
                index_to_hadm[str(chunks.iloc[index, 1])] = chunks.iloc[index, 3]
            # # index_id = chunks["INDEX"][index]
            # if index_id in chunks["ROW_ID"]:
            #     row_id = chunks["ROW_ID"][index_id]
            #     hadm_id = chunks["HADM_ID"][index_id]
            #
            # else:
            #     print("Index id is not in HADM_ID Series")

    output = []
    with open(filename, 'r') as reader:
        lines = reader.readlines()
    count_matched = 0
    count_unmatched = 0
    bad_records = 0
    for line in lines[1:]:
        array = line.split(",")
        if len(array) > 3:
            if str(array[1]) in index_to_hadm:
                hadm_id = index_to_hadm[str(array[1])]
                count_matched += 1
            else:
                print(f"hadm is missing for {array[1]}")
                hadm_id = ""
                count_unmatched += 1
            output.append(str(array[0]) + "," + str(array[1])
                          + "," + str(array[2])
                          + "," + str(hadm_id)
                          + "," + " ".join(array[3:]))
        else:
            bad_records += 1
            #output.append(line)

    with open(filename + "-fix.csv", 'w') as writer:
        writer.write("INDEX,ROW_ID,SUBJECT_ID,HADM_ID,SYMPTOMS\n")
        writer.write("".join(output))

    print(f"count_matched: {count_matched}, count_unmatched: {count_unmatched}, bad_records: {bad_records}")


if __name__ == "__main__":
    main("../data/symptoms-batch5.csv")
