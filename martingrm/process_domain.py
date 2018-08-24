"""Makes sure the specific domain terms are correctly translated"""

import json
import sys
import numpy as np
import re
import fileinput
from martingrm.martin_helper import tf_to_numpy_ATT_Matrix

def process_domain_correspondence(src_file, dst_file, attention_file, domain_dictionary_file="./domain_dictionary.json"):
    dictionary = {}

    with open(domain_dictionary_file) as f:
        dictionary = json.load(f)

    """
    The original sentences are read and their words are checked with the domain dictionary. The matching
    words are replaced by their equivalent words from the dictionary.
    """
    with open(attention_file) as att:
        attention_matrices = att.readlines()

        with open(src_file) as f:
            for lineNumber, line in enumerate(f):
                for wordNumber, word in enumerate(line.split()):
                    if word in dictionary:
                        attention_matrix = tf_to_numpy_ATT_Matrix(attention_matrices[lineNumber])
                        index = np.argmax(attention_matrix[wordNumber])
                        with fileinput.FileInput(dst_file, inplace=True, backup='.bak') as file:
                            counter = 0
                            for l in file:
                                if counter == lineNumber:
                                    sentence = l.split()
                                    sentence[index] = dictionary[word]
                                    for wrd in sentence:
                                        print(wrd+" ", end='')
                                    print("")
                                else:
                                    print(l, end='')
                                counter = counter + 1
