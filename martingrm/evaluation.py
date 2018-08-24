#!/usr/bin/env python3

import nltk
import linecache
import json
from martingrm.Unknown import Unknown
from martingrm.Unknown import MyEvaluationEncoder


if __name__ == '__main__':
    from sys import argv

    nmt_output = ""
    martin_output = ""
    target_lang_file = ""
    alignments_file = ""
    unknowns_log_file = ""

    for arg in argv:
        if "original_output_file" in arg:
            for i, character in enumerate(arg):
                if character == '=':
                    nmt_output = arg[i+1:]
                    break
        elif "secondary_output_file" in arg:
            for i, character in enumerate(arg):
                if character == '=':
                    martin_output = arg[i+1:]
                    break
        elif "target_lang_file" in arg:
            for i, character in enumerate(arg):
                if character == '=':
                    target_lang_file = arg[i+1:]
                    break
        elif "alignments_file" in arg:
            for i, character in enumerate(arg):
                if character == '=':
                    alignments_file = arg[i+1:]
                    break
        elif "unknowns_log_file" in arg:
            for i, character in enumerate(arg):
                if character == '=':
                    unknowns_log_file = arg[i+1:]
                    break

    ####### START EVALUATION

    ## ALIGNMENT EVAL
    correct_words = 0
    incorrect_words = 0

    replacedUnks = []

    with open(unknowns_log_file) as f:
        replacedUnks = json.load(f)

    for unk in replacedUnks:
        alignments = linecache.getline(alignments_file, int(unk['sentenceNumber'])+1).split()
        startingPrefix = str(unk['originalWordNumber'])+"-"
        matching = [s for s in alignments if s.startswith(startingPrefix)]
        if (len(matching) != 1):
            print("NOT FOUND \t" + str(unk['originalWordNumber']) +"-? \t in " + str(alignments))
            continue
        tgt_line = linecache.getline(target_lang_file, int(unk['sentenceNumber'])+1).split()
        word_alignment = matching[0].split("-")
        if (tgt_line[int(word_alignment[1])] == str(unk['translation'])):
            correct_words = correct_words + 1
            print("OK \t-\t"+tgt_line[int(word_alignment[1])]+" == "+str(unk['translation']))
        else:
            incorrect_words = incorrect_words + 1
            print("ERROR \t-\t"+tgt_line[int(word_alignment[1])]+" -> "+str(unk['translation']))


    ## BLEU EVAL
    references = [line.rstrip('\n') for line in open(target_lang_file)]
    hypothesis1 = [line.rstrip('\n') for line in open(nmt_output)]
    hypothesis2 = [line.rstrip('\n') for line in open(martin_output)]
    BLEUscore_nmt = 0
    BLEUscore_martin = 0

    numLines = len(references)

    if (numLines == len(hypothesis1) and numLines == len(hypothesis2)):
        i = 0
        while i < numLines:
            references[i] = [references[i].split()]
            hypothesis1[i] = hypothesis1[i].split()
            hypothesis2[i] = hypothesis2[i].split()
            i += 1
        BLEUscore_nmt = nltk.translate.bleu_score.corpus_bleu(references, hypothesis1)
        BLEUscore_martin = nltk.translate.bleu_score.corpus_bleu(references, hypothesis2)
    else:
        print("Input files don't have the same amount of sentences.")


    print("\n\n\n\n\n-------------ALIGNMENTS COUNT---------------\nCorrectly translated: "+str(correct_words)+"\nIncorrectly translated: "+str(incorrect_words)+"\n")
    print("---------------BLEU---------------\nNMT BLEU: " + str(BLEUscore_nmt) + "\nMartin BLEU: "+ str(BLEUscore_martin)+"\n------------------------------\n")
