'''
Pauli Xu "txtclean_Austen" (June 2016)

For Stanford dependency parsing, clean Jane Austen text from Project
Gutenberg, store it in small chunks into .txt files, and parse it.'''

'''
reads from current folder a text with given title.
stores _chunks and _parses into subdirectories of current folder
'''


import string
import re
import subprocess
from sys import exit
from nltk.tokenize import sent_tokenize

single_quotes = False

#path to shell executable of Core NLP
nlp_executable = "/Users/dhlabadministrator/PX/Lib/stanford-corenlp-full-2015-12-09/corenlp.sh"

output_form = "json"





#NOTE: edit 7/26/16 try to loop over several Austen texts. Moved everything 
#below to the left.
titles = ["Austen-Emma", "Austen-Pride"]

for title in titles:


    #read full text file.                ASSUME: no header stuff. 
    folder = "texts/"
    #title = "Austen-Pride"
    filename = folder + title + ".txt"

    f = open(filename, 'r')     #ADD: looping over titlenames?
    text = f.read()                    #ADD: filesize restriction?
    f.close()

    #To clarify things for the dependency parser, remove stylistic characters
    #and substitute full sentence characters with a period '.'

    ##eyeballed three sentences: seems to be able to deal with -- quite well.

    periodchar = [";"]    #; leaves some sentences starting in lower case
    for char in periodchar:
        text = text.replace(char, ".")

    badchar = ['_', "Mr. ", "Mrs. ", "\r"]
    for char in badchar:
        text = text.replace(char, "")

    newline = ["\n"]
    for nl in newline:
        text = text.replace(nl, " ")

    #remove single dashes '-'
    text = re.sub(r"([^-])-([^-])", r"\1\2", text)


    #some books use ' ' for speech.  E.g. "Hard Times" on Gutenberg.
    #replace if single quote at start/end of line or pre/post white space or
    #comma.
    if single_quotes == True:       #ADD: optional argument to function. 
        text = re.sub(r"(.)'([^a-zA-Z0-9])", r'\1"\2', text)  #end of quote
        text = re.sub(r"([^a-zA-Z0-9])'(.)", r'\1"\2', text)  #start of quote
        text = re.sub(r"^'|'$", "\"", text)                #start/end of line

    #remove narrative interjections between quotations. "Momma," I said "..."
    #note: there are quotations that end in -- , instead of ". So need other
    #methods. 

    text = text.split("\"")     #split by " into blobs of quotes/non-quotes
    #remove empty/whitespace lines (consecutive quotes)
    text = [blob for blob in text if blob.strip()]
    #remove interjections between quotes. 
    #interpret as chunks that start with a space and a lowercase. 

    text_clean = ['.'] #start with placeholder to avoid index error
    skip = False
    for i, blob in enumerate(text):
        if (i != 0 and i != len(text) and blob[0] == ' ' and blob[1].islower()):
            text_clean[-1] = text[i-1] + ' ' + text[i+1]
            skip = True
        else:
            if skip:
                skip = False
            else:
                text_clean += [blob]

    #split into sentences, then chunks, to store them as parsable files. 
    #(now chunks by # of sentences. Alternatively have a threshold # of words, 
    #that is sum of len(snt)
    text_snt = []
    for blob in text_clean:
        text_snt += sent_tokenize(blob)

    chunk_size = 5      #number of sentences in a chunk
    text_chunks = [text_snt[i:i+chunk_size] for i in range(0, len(text_snt),
                                                           chunk_size)]




    '''storing text'''





    #mk directory for parsed files. Write chunks/groups of clean sentences 
    #into files
    cur_dir = subprocess.check_output(["pwd"])
    cur_dir = cur_dir.replace("\n", "")
    chunks_dir = cur_dir + "/" + title + "_chunks"
    parses_dir = cur_dir + "/" + title + "_parses"

    try:
        subprocess.check_call(["mkdir", chunks_dir, parses_dir])
    except subprocess.CalledProcessError as e:
        print e
        print "but let's continue"

    for k, chunk in enumerate(text_chunks):
        filename = str(k) + title + ".txt"
        f = open(chunks_dir + "/" + filename,'w')
        f.write(' '.join(chunk))
        f.close()
        total_files = k



    #Run NLP on the clean sentence files. OS commands are run from subprocess
    #module.

    #core_nlp command line calling. Be careful about whitespaces. 
    #Note: StanfordCoreNLP refuses to be found with specified path names.
    #Workaround: change directories to the directory with the CoreNLP library,
    #produce files there, then transport them back. 
    #(also note: annotators 'relation, natlog,ner' affect the performance of
    #'depparser', even if I don't use relations on their own.)

    for filenum in range(0, total_files):
        filename = str(filenum) + title + ".txt"
        nlp_cmd = nlp_executable + " "
        nlp_cmd += "-Xmx2g" + " "       #memory, max RAM. 2g == 2gb.
        nlp_cmd += "-annotators \
                tokenize,ssplit,pos,lemma,ner,parse,depparse" + " "
        nlp_cmd += "-file" + " " + chunks_dir + "/" + filename + " "
        nlp_cmd += "-outputFormat" + " " + output_form
        nlp_cmd = nlp_cmd.split(" ")
        try:
            subprocess.check_call(nlp_cmd)
        except subprocess.CalledProcessError:
            sys.exit("nlp failed at filenum " + str(filenum))

    mv_cmd = "mv *" + title + ".txt." + output_form +" " + parses_dir
    proc = subprocess.Popen(mv_cmd, shell=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)

    ###clean up characters character-wise. Python doesn't seem to support 
    #this kind of thinking...
    #text_chars = ""
    #
    #for i, char in enumerate(text):
    #    if skip:
    #        continue
    #    elif char in periodchar:
    #        text_chars += "."
    #    elif char in newline:
    #        text_chars += " "
    #    elif char == '-' and text[i+1] == '-':
    #        skip = True
    #    elif char in badchar:
    #        continue
    #    else:
    #        text_chars += char

    ##split by quotations and non-quotations (=narrations).
    #starts_with_quotes = (text[0][0] == '\"')        #check if first char is \"
    #text = text.split("\"")
    #if starts_with_quotes:
    #    text_quotes = text[0::2]
    #    text_narration = text[1::2]
    #else:
    #    text_narration = text[0::2]
    #    text_quotes = text[1::2]
    #
    ##from narration, Remove empty strings.(Caused by continuous dialogue.
    ##E.g."why?" "because?"). Remove incomplete sentences (method: check 
    ##lowercase first character)(note space, not lower or upper case).
    #text_narration = filter(None, text_narration)
    #text_narration = [snt for snt in text_narration if snt0.islower()]
    #
    ##MAYBE remove spaces
    #
    ##in quotations, connect setnences broken by narrative interjection. 
    ##E.g. "Mamma," she said, " why so?". (method: If a sentence starts with 
    ##lower case, concatenate it to preceding sentence)








