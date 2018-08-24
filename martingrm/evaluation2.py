#!/usr/bin/env python3

import linecache


if __name__ == '__main__':
    from sys import argv

    martin_output = ""
    source_lang_file = ""
    alignments_file = ""

    for arg in argv:
        if "output_file" in arg:
            for i, character in enumerate(arg):
                if character == '=':
                    martin_output = arg[i+1:]
                    break
        elif "source_lang_file" in arg:
            for i, character in enumerate(arg):
                if character == '=':
                    source_lang_file = arg[i+1:]
                    break
        elif "alignments_file" in arg:
            for i, character in enumerate(arg):
                if character == '=':
                    alignments_file = arg[i+1:]
                    break

    ####### START EVALUATION

    ## ALIGNMENT EVAL
    correct_words = 0
    incorrect_words = 0

    replacedUnks = []

    with open(source_lang_file) as src:
        for lineNumber, line in enumerate(src):
            for wordNumber, word in enumerate(line.split()):
                if word == "després":
                    alignments = linecache.getline(alignments_file, lineNumber+1).split()
                    startingPrefix = str(wordNumber)+"-"
                    matching = [s for s in alignments if s.startswith(startingPrefix)]
                    if (len(matching) != 1):
                        print("NOT FOUND")
                        continue
                    tgt_line = linecache.getline(martin_output, lineNumber+1).split()
                    word_alignment = matching[0].split("-")
                    if (tgt_line[int(word_alignment[1])] == "<después>"):
                        correct_words = correct_words + 1
                        #print("OK \t-\t"+tgt_line[int(word_alignment[1])]+" == "+str(unk['translation']))
                    else:
                        incorrect_words = incorrect_words + 1
                        print("ERROR \t-\t"+tgt_line[int(word_alignment[1])])


    print("\n\n\n\n\n-------------ALIGNMENTS COUNT---------------\nCorrectly translated: "+str(correct_words)+"\nIncorrectly translated: "+str(incorrect_words)+"\n")
    #print("---------------BLEU---------------\nNMT BLEU: " + str(BLEUscore_nmt) + "\nMartin BLEU: "+ str(BLEUscore_martin)+"\n------------------------------\n")
