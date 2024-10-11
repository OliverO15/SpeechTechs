orfeo_string = ""

f = open("./corpus_fr/01_OG_NH_100222.orfeo", "r")
# print(f.read())
orfeo_string = f.read()
f.close()

# print(orfeo_string)

orfeo_split = orfeo_string.split("\n\n")

segments = []

# Loop through each section and process it
for section in orfeo_split:
    # Split the section by line breaks
    lines = section.strip().split('\n')
    print(lines)

    if (len(lines) < 2):
        continue

    id = lines[0].split(' = ')[1].strip()
    sentence = lines[1].split(' = ')[1].strip()

    print('ID: ', id)
    print('Sentence: ', sentence)

    # First Word
    first_word = lines[2].split("\t")[1].strip()


# Print each segment in the list
# for segment in segments:
#     print(segment)
