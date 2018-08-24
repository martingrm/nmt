#!/usr/bin/env python3

import os
import subprocess

domainFile = "./domain_dictionary.json"
unknownsFile = "./known"
embeddingsFile = "./embeddings_output"
attentionFile = "./attention_output"
alignmentsFile = "./alignments"
referenceFile = "./reference.txt"

if __name__ == '__main__':
    from sys import argv

    unks = True
    dominio = True

    inputFile = "input.txt"
    inputFileArgPOS = -1
    outputFile = "output.txt"
    outputFileApp = "outputFilePart.txt"

    arguments = ""
    for arg in argv:
        if (arg == "run.py"):
            continue
        elif ("-unknown" in arg):
            eqPos = -1
            for i, character in enumerate(arg):
                if character == '=':
                    eqPos = i
                elif eqPos != -1:
                    if character == "0" or character == 'f' or character == 'F':
                        unks = False
                    break
        elif ("-domain" in arg):
            eqPos = -1
            for i, character in enumerate(arg):
                if character == '=':
                    eqPos = i
                elif eqPos != -1:
                    if character == "0" or character == 'f' or character == 'F':
                        dominio = False
                    break
        else:
            if "input_file" in arg:
                for i, character in enumerate(arg):
                    if character == '=':
                        inputFile = arg[i+1:]
                        break
                continue
            elif "output_file" in arg:
                for i, character in enumerate(arg):
                    if character == '=':
                        outputFile = arg[i+1:]
                        break

            arguments = arguments + str(arg) + " "

    print("Unknowns: " + str(unks) + "\nDiccionario de Dominio: " + str(dominio))

    nmtCommand = "python -m nmt.nmt " + arguments
    wcCommand = "wc -l " + inputFile + " | tr -dc '0-9'"
    outputAppenderCommand = "cat " + outputFile + " >> " + outputFileApp + " && cat " + outputFileApp + " > " + outputFile
    wcProcess = subprocess.Popen(wcCommand, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    lineCount, error = wcProcess.communicate()
    if int(lineCount) == 1:
        print("We're Ready to translate!\n" + nmtCommand + " --inference_input_file="+inputFile)
        process = subprocess.Popen(nmtCommand + " --inference_input_file="+inputFile, shell=True)
        process.communicate()
    else:
        with open(inputFile) as inpFile:
            for i, line in enumerate(inpFile):
                with open("inpFilePart.txt", "w") as fw:
                    fw.write(line)
                print("Translating sentence #" + str(i))
                with open(os.devnull, 'w') as FNULL:
                    process = subprocess.Popen(nmtCommand+ " --inference_input_file=inpFilePart.txt", shell=True, stdout=FNULL, stderr=FNULL)
                    _, error = process.communicate()
                    if error:
                        print("-- ERROR --")
                        print(error)
                        import sys
                        sys.exit()
                process = subprocess.Popen(outputAppenderCommand, shell=True, stdout=None, stderr=None)
                process.communicate()

    if dominio:
        from martingrm.process_domain import process_domain_correspondence
        print("\n\nProcesing domain specific words...")
        process_domain_correspondence(inputFile, outputFile, attentionFile, domainFile)
    if unks:
        from martingrm.get_unk_emb import get_unknowns
        argsUnk = {}
        argsUnk['-trans'] = outputFile
        argsUnk['-emb'] = embeddingsFile
        argsUnk['-att'] = attentionFile
        argsUnk['-out'] = unknownsFile
        argsUnk['-src'] = inputFile
        argsUnk['-aligns'] = alignmentsFile
        argsUnk['-ref'] = referenceFile
        print("\n\nProcesing unknowns...")
        get_unknowns(argsUnk)


    # CLEANUP
    with open(os.devnull, 'w') as FNULL:
        cleanUpCommand = "rm ../traduccion.txt.bak attention_* embeddings_output inpFilePart.txt " + outputFileApp
        process = subprocess.Popen(cleanUpCommand, shell=True, stdout=FNULL, stderr=FNULL)
        process.communicate()
