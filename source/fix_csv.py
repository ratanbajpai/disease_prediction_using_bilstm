

def main(filename):
    output = []
    with open(filename, 'r') as reader:
        lines = reader.readlines()

    for line in lines:
        print(line)
        array = line.split(",")
        if len(array) > 4:
            output.append(array[0] + "," + array[1] + "," + array[2] + "," +  " ".join(array[3:]))
        else:
            output.append(line)

    with open(filename + "-fix.csv", 'w') as writer:
        writer.write("".join(output))


if __name__ == "__main__":
    main("../data/Symptoms.batch1.csv")