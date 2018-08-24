"""Collect the embeddings for unknown words"""

import json
import sys
import numpy as np
import re
import fileinput
import linecache
from martingrm.Unknown import Unknown
from martingrm.Unknown import MyEncoder
from martingrm.Unknown import MyEvaluationEncoder
from martingrm.martin_helper import tf_to_numpy_ATT_Matrix


def replace_word(unk, trans, transFile):
    with fileinput.FileInput(transFile, inplace=True, backup='.bak') as file:
        counter = 0
        for line in file:
            if counter == unk.sentenceNumber:
                sentence = line.split()
                sentence[unk.wordNumber] = trans
                for word in sentence:
                    print(word+" ", end='')
                print("")
            else:
                print(line, end='')
            counter = counter + 1

def get_unknowns(myargs):
    counter = 1
    unknowns = {}
    logUnksReplaced = []
    unkEmbeddings = []
    knownUnks = []
    manualMode = False #myargs.get('-learnMode', True)
    alignMode = True #myargs.get('-learnMode', True)
    to_ignore = []

    if not '-trans' in myargs or not '-emb' in myargs or not '-out' in myargs or not '-att' in myargs or not '-src' in myargs:
        print("ERROR. You need to specify the paramters as follows:\n")
        print("-trans translation_file.txt -src original_sentence.txt -emb embeddings_file.txt -att attention_output.txt -out storedData.txt")
        sys.exit()


    with open(myargs['-out']) as f:
        knownUnks = json.load(f)

    """
    The translation is read. The embeddings are saved one per line in the same order they appear on the sentences
    (with an extra embedding per sentence at the end for the </s>), so the position of each <unk> fond
    on the translation is stored so that later we can retrieve its embeddings.
    """
    with open(myargs['-trans']) as f:
        for lineNumber, line in enumerate(f):
            for wordNumber, word in enumerate(line.split()):
                if (word == "<unk>"):
                    unknowns[counter] = Unknown(line, lineNumber, wordNumber)
                counter = counter + 1
            counter = counter + 1


    counter = 1
    with open(myargs['-att']) as att:
        with open(myargs['-src']) as src:
            originals = src.readlines()
            attention_matrices = att.readlines()

            for key, value in unknowns.items():
                attention_matrix = tf_to_numpy_ATT_Matrix(attention_matrices[value.sentenceNumber])
                attention_matrix = attention_matrix.transpose()
                index = np.argmax(attention_matrix[value.wordNumber])
                unknowns[key].set_original_sentence(originals[value.sentenceNumber])
                unknowns[key].set_original(originals[value.sentenceNumber].split()[index])
                unknowns[key].set_original_wordNumber(index)



    """
    Afterwards, we analize the embeddings and store the ones corresponding to <unk>s
    """
    with open(myargs['-emb']) as f:
        for i, line in enumerate(f):
            if i+1 in unknowns:
                line = re.sub(r'\[\[', "[", line)
                line = re.sub(r'\]\]', "]", line)
                unknowns[i+1].set_embedding(line)


    for key, value in unknowns.items():
        found = ""
        euclFound = 8.0
        for knownWord in knownUnks:
            knownEmbedding = np.array(json.loads(knownWord['embedding']))
            unknownEmbedding = np.array(json.loads(value.embedding))
            euclidean_distance = np.linalg.norm(knownEmbedding-unknownEmbedding)
            if euclidean_distance < euclFound:
                found = knownWord['translation']
                euclFound = euclidean_distance

        if found != "":
            replace_word(value, found, myargs['-trans'])
            print(value.original + " -> " + found)
            unknowns[key].set_translation(found)
            to_ignore.append(key)
            logUnksReplaced.append(value)
        elif manualMode:
            print("In ", end='')
            print(value.originalSentence, end='')
            trans = input("How would you say \"" + value.original + "\"? ")
            replace_word(value, trans, myargs['-trans'])
            unknowns[key].set_translation(trans)
            print("")
            # Comment from here to the end of the else in order not to update the knownUnks each time a new unknown is added ("learned")
            newEntry = unknowns[key]
            knownUnks.extend([newEntry])
            with open(myargs['-out'], "w") as fw:
                json.dump(knownUnks, fw, cls=MyEncoder)
            with open(myargs['-out']) as f:
                knownUnks = json.load(f)
        elif alignMode:
            alignments_line = linecache.getline(myargs['-aligns'], value.sentenceNumber+1).split()#x-y
            source_line = linecache.getline(myargs['-src'], value.sentenceNumber+1).split() #catalan = x
            reference_line = linecache.getline(myargs['-ref'], value.sentenceNumber+1).split() #espanol = y

            #print("Sentence: " + str(value.sentenceNumber))
            #print("Word: " + str(value.originalWordNumber))
            #print("Alignment line: " + str(len(alignments_line)))
            startingPrefix = str(value.originalWordNumber)+"-"
            matching = [s for s in alignments_line if s.startswith(startingPrefix)]
            if (len(matching) != 1):
                print("NOT FOUND \t" + str(value.originalWordNumber)+"-? \t in " + str(alignments_line))
                continue
            word_alignment = matching[0].split("-")
            trans = reference_line[int(word_alignment[1])]
            replace_word(value, trans, myargs['-trans'])
            unknowns[key].set_translation(trans)
            newEntry = unknowns[key]
            knownUnks.extend([newEntry])
            with open(myargs['-out'], "w") as fw:
                json.dump(knownUnks, fw, cls=MyEncoder)
            with open(myargs['-out']) as f:
                knownUnks = json.load(f)
            print(value.original + " -> " + value.translation)



    with open("./log_replacement.txt", "w") as logW:
        json.dump(logUnksReplaced, logW, cls=MyEvaluationEncoder)

    # Uncomment this in order to update the knownUnks only once at the end of the batch eval
    """
    for key in to_ignore:
        del unknowns[key]

    # add the new known words to the storage
    knownUnks.extend(list(unknowns.values()))


    with open(myargs['-out'], "w") as fw:
        json.dump(knownUnks, fw, cls=MyEncoder)
    """
