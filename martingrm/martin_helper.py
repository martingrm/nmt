import sys
import numpy as np
import json
import re


def tf_to_numpy_ATT_Matrix(original):
    original = re.sub(r'\]\]\]\, \[\[\[', "]]\n[[", original)
    original = re.sub(r'\[\[\[\[', "[[", original)
    original = re.sub(r'\]\]\]\]', "]]", original)
    original = re.sub(r'\]\[', ",", original)
    original = re.sub(r'\]\, \[', ",", original)
    matrix = np.array(json.loads(original))
    #result = matrix.transpose() # done outside this function whenever needed
    return matrix
