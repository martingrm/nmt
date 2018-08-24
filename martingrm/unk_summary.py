"""Collect the embeddings for unknown words"""

import json
import sys
import numpy as np
import re
import fileinput
import linecache
from martingrm.Unknown import Unknown
from martingrm.Unknown import MyEvaluationEncoder
from martingrm.martin_helper import tf_to_numpy_ATT_Matrix

def get_unknowns(myargs):
    counter = 1
    unknowns = {}
    unkEmbeddings = []
    knownUnks = []
    logUnksReplaced = []
    manualMode = False #myargs.get('-learnMode', True)
    alignMode = True #myargs.get('-learnMode', True)
    to_ignore = []

    if not '-trans' in myargs or not '-emb' in myargs or not '-out' in myargs or not '-att' in myargs or not '-src' in myargs:
        print("ERROR. You need to specify the paramters as follows:\n")
        print("-trans translation_file.txt -src original_sentence.txt -emb embeddings_file.txt -att attention_output.txt -out storedData.txt")
        sys.exit()

    """
    The translation is read. The embeddings are saved one per line in the same order they appear on the sentences
    (with an extra embedding per sentence at the end for the </s>), so the position of each <unk> fond
    on the translation is stored so that later we can retrieve its embeddings.
    """
    with open("../traduccion_nmt.txt") as f:
        for lineNumber, line in enumerate(f):
            for wordNumber, word in enumerate(line.split()):
                if (word == "<unk>"):
                    unknowns[counter] = Unknown(line, lineNumber, wordNumber)
                counter = counter + 1
            counter = counter + 1


    counter = 1
    with open(myargs['-att']) as att:
        with open(myargs['-src']) as src:
            with open("../traduccion_martin.txt") as mart:
                originals = src.readlines()
                attention_matrices = att.readlines()
                martins = mart.readlines()

                for key, value in unknowns.items():
                    attention_matrix = tf_to_numpy_ATT_Matrix(attention_matrices[value.sentenceNumber])
                    attention_matrix = attention_matrix.transpose()
                    index = np.argmax(attention_matrix[value.wordNumber])
                    unknowns[key].set_original_sentence(originals[value.sentenceNumber])
                    unknowns[key].set_original(originals[value.sentenceNumber].split()[index])
                    unknowns[key].set_original_wordNumber(index)
                    translation = martins[value.sentenceNumber].split()[value.wordNumber]
                    if translation != "<unk>":
                        unknowns[key].set_translation(translation)
                        print(value.original + " -> " + value.translation)
                        logUnksReplaced.append(value)

    with open("./log_replacement.txt", "w") as logW:
        json.dump(logUnksReplaced, logW, cls=MyEvaluationEncoder)
