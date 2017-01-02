'''7/7/16 Pauli Xu
Build_chain_dict.py v.0.1

an executable.

use json_parser for all parsed files of given text title. Store
dictionary-json-file in some sizable chunks. 
'''



#create storage dict
from collections import defaultdict
#would like sets, but there's some under-the-hood error. Could convert to set
#later.

#instantiate jsonparser class.
from classes.j import json_parser


#run j.phrase_collect_and_store(phrase_dict) for all title-filenum-sent_id,
#write json.
import json
import glob
import re

titles = ["Austen-Mansfield", "Austen-Love", "Austen-Lady", "Austen-Pride",
          "Austen-Emma"] 

#accepted_items 7/14: ['phrase', 'branch']
item_type = 'branch'

#for accepted types, see classes/j.py meth give_dict_key() 
key_types = ['hctype', 'tree_branch_id']

for title in titles:
    folder = title + '_parses/' #folder with parse files to read filenames.
    for key_type in key_types:
        phrase_dict = defaultdict(list)
        i=0; k=0
        for parsefile in glob.iglob(folder + '[0-9]*' + title +'.txt.json'):
            #counter for processed files
            i += 1
            if (i > 500 * k):
                print(title, " ", i, "files processed")
                k += 1
            #store filenum from filename
            filenum = int(re.findall('[0-9]+', parsefile)[0])
            print("filenum: ", filenum)
            #instantiate json_parser
            j = json_parser(title, filenum)
            for sent_id in j.sent_ids:
                print("sent_id: ", sent_id)
                j.update_sent_inst_variables(sent_id)
                j.collect_and_store(phrase_dict, item_type, key_type)

        store = json.dumps(phrase_dict, sort_keys=True, indent=4, separators=(',', ': '))
        filename = title +'_' + item_type + '_' + key_type + ".dict.json"
        f = open(filename, 'w')
        f.write(store)
        f.close()


#If want to iterate in chunks:
#for bot in range(0, last_filenum+1, step):
#    print("bot: ", bot)
#    phrase_dict = defaultdict(list)
#    for filenum in range(bot,bot+step):
#step = last_filenum + 1 #probably redundant 1, since there is one below

#Add to name: str(bot) + "-" + str(bot+step-1)\

#move dict files to dict folder
import subprocess
from sys import exit

dict_folder = "dict_jsons"
mv_cmd = "mv *.dict.json" + " " + dict_folder
proc = subprocess.Popen(mv_cmd, shell=True, stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)

'''gather loop_deps (json files with dependency loops)'''
#
#loop_dict = defaultdict(list)
#for filenum in range(0,last_filenum+1):
#    print("filenum: ", filenum)
#    j = json_parser(title, filenum)
#    for sent_id in j.sent_ids:
#        print("sent_id: ", sent_id)
#        j.update_sent_inst_variables(sent_id)
#        j.loop_deps(loop_dict)
#store = json.dumps(loop_dict, sort_keys=True, indent=4, separators=(',', ': '))
#filename =  title + ".loop_dict.json"
#f = open(filename, 'w')
#f.write(store)
#f.close()
#
##move loop_dict files to loop_dict folder
#loop_dict_folder = "loop_dict_jsons"
#mv_cmd = "mv *.loop_dict.json" + " " + loop_dict_folder
#proc = subprocess.Popen(mv_cmd, shell=True, stdout=subprocess.PIPE,
#                        stderr=subprocess.PIPE)
