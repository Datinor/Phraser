#Pauli Xu, 7/7/16, v.0.3
#json_parser.py
#For input, take a json file that was parsed by 
#Stanford CoreNLP dependency parser.
#convert the info in json file into various lists/dictionaries/trees in Python


#currently functions are both for data exploration and helping other functions. 
#in the future, for speed, have separate helper functions that return 
#only the necessary information. Have exploration functions call these same
#smaller helper functions

'''
make this a class. 
functions:
    json reader (instantiated with 
    instance variable variables definer
    have json_parsing as a module?
            -right now there are many functions that depend on
            instance variable variables based on json file. 
'''

'''Terminology (incomplete list)
phrase/tree ~ branch (a tree with a higher node)

governor/head

dependent/modifier

dependency/relation

dependency chain/nested list (of phrases)/ tree and branches
'''



#the comment below should be within json_parser, but then vim editor 
#complains about indentation
'''given a json file,
read it and initiate sentence 0 instance variables (instantiate class)
'''
class json_parser:

    def __init__(self, title, filenum):
        #aim to read parsed json file:
        json = __import__('json')
        #construct filename, e.g. Austen-Pride_parses/2Austen-Pride.txt.json
        self.filenum = str(filenum)
        self.title = title
        folder = title + "_parses/"
        filetype = ".txt.json"
        filename = folder + self.filenum + title + filetype

        #read json
        f = open(filename, 'r')
        json_string = f.read()
        f.close()

        #count existing sentences. store json as list
        self.parsed_json = json.loads(json_string)
        self.sent_ids = range(0, len(self.parsed_json['sentences']) - 1)

        #initialize sentence instance variables with sentence 0.
        self.update_sent_inst_variables(0)

    #swap sentence-instance variable-variables into those of the given sentence
    def update_sent_inst_variables(self, sent_id):
        sent_json = self.parsed_json['sentences'][sent_id]
        self.json_deps = sent_json['collapsed-ccprocessed-dependencies']
        self.json_toks = sent_json['tokens']
        self.json_toks_text = [token['originalText'] for token in self.json_toks]
        self.sent_id = sent_id

    '''Given a sentence,
    function to access governors
    '''
    #return list of all governors in sentence
    def govs(self):
          return sorted(set([dep_token['governor'] for dep_token in self.json_deps]))


    '''Given a sentence and word id_list,
    functions to translate ids into token info. (words, POS, etc.)
    '''
    #translate into POS. 
    #Return list (of strings)
    def POS(self, id_list):
        return [word_dict['pos'] for word_dict in self.json_toks
                                    if word_dict['index'] in id_list]

    #translate into words. Allow nested lists of ids.
    #Return (nested) list (of strings)
    def text(self, id_list):
        #if id_list is all integers, 
        #just find correponding indices from json_toks
        if all(isinstance(item, int) for item in id_list):
            return [self.json_toks[index-1]['originalText'] for index in
                    id_list]
        #if id_list is nested list of ids, fetch id or recurse on the list.
        else:
            words = []
            for ele in id_list:
                if isinstance(ele, int): #if int,fetch word. token order 0-based
                    words += [self.json_toks[ele - 1]['originalText']]
                elif isinstance(ele, list):
                    words += [self.text(ele)]
                elif isinstance(ele, tuple):
                    words += [tuple(self.text(list(ele)))] #ugly solution, will do
                else:
                    words += [ele]
            return words



    """Given a sentence and governor,
    functions to access dependents."""

    #find ids of dependents
    #return list of ints
    def dep_ids(self, gov):
        return [dep_token['dependent']
                for dep_token in self.json_deps if dep_token['governor'] == gov]

    #find dependencies. If given id_list, only translate those
    #return list of strings
    def dep_types(self, gov, id_list = range(1,100)):
        return [dep_token['dep']
                for dep_token in self.json_deps 
                if dep_token['governor'] == gov
                and dep_token['dependent'] in id_list]

    #find dependents
    #return list of pairs (int, string)
    def dep_id_types(self, gov):
        return [(dep_token['dependent'], dep_token['dep'])
                for dep_token in self.json_deps if dep_token['governor'] == gov]

    #find ids of dependents that are also governors
    #return list of ints
    def dep_also_govs(self, gov, types=False):
        if not types:
            return [dep_id for dep_id in self.dep_ids(gov) if dep_id in self.govs()]
        else:
            return [dep_type for (dep_id, dep_type) in self.dep_id_types(gov) 
                    if dep_id in self.govs()]

    '''Given sentence,
    Construct phrase-nodes to store in a dictionary. 
        Use the following format:
            [(dep to previous gov), (phrase with full info), (orig filenum, -name,
             sentence id)]
        with parts expanded:
            (dep to previous gov)-->
                (dep_type, prev_gov_word, POS of prev_gov, 
                 gov/phrase head of this phrase)
            (phrase with full info)-->
                [(dep_type, dependent_word, POS of dependent, 
                lemma, leaf or root or branch_dep_id) ...]
            (orig filenum, name, sentence id)-->
                as is.
    '''


    #Take defaultdict(list). (create def_dict(list) of dictionaries)
    #operation: starting from the *dependents* of gov, recursively store 
    #phrase/branch information as specified above. Check for verb chains.
    #store results as tuples into dictionary, keyed by dep_type. 
    #Return nothing, only update dictionary. 
    #(point of confusion: the loop variable "dep" refers to id, not type)

    #Edit: 7/8, Python doesn't support recursion. Modified to a stack-list 
    #iteration
    #Edit 7/14: item_types. 'phrase' is described above. 'branch' is a
    #dictionary with branch pointer
    def collect_and_store(self, def_dict, item_type='phrase', 
                                          key_type='tree'):
        from collections import defaultdict
        #check that item_type is accepted
        accepted_items = ['branch', 'phrase']
        if item_type not in accepted_items:
            print("item type not in ", accepted_items)
        govstack=[0]
        #check for seen_nodes (circular governor relationships)
        #causing inf. loop
        seen_nodes = []
        while govstack:
            gov = govstack.pop()
            seen_nodes += [gov]
            #check for chained verbs
            gov_word, deps_to_skip = self._word_and_chained_verbs(gov)
            #mark gov POS
            if gov != 0:
                gov_pos = self.POS([gov])[0]
            else:
                gov_pos = 'ROOT'
            deps_to_store = [dep_g for dep_g in self.dep_also_govs(gov) 
                             if dep_g not in deps_to_skip
                             and dep_g not in seen_nodes]
            for dep in deps_to_store:
                govstack.append(dep)
                #POSSIBLE KEYS. CHANGEABLE.
                key = self.give_dict_key(key_type, dep)

                sub_dict = defaultdict(list)
                if item_type == 'phrase':
                    self.phrase_store(sub_dict, dep)
                elif item_type == 'branch':
                     self.branch_info_store(sub_dict, dep)
                def_dict[key].append(sub_dict)

    #give key of demanded type. dep is the branch token id given in 
    #wrapper function collect_and_store()
    def give_dict_key(self, key_type, dep):
        #tree id (source)
        if key_type == 'tree_branch_id':
            key = '_'.join(self.Tree_id()) + '_' + str(dep)
        #head and child types, smushed into continuous string
        elif key_type == 'hctype':
            key = self.branch_hctype(dep)
        #head type
        elif key_type == 'head':
            key = self.parent(dep,type=True)
        elif key_type == 'branches':
            key = '/'.join(self.branch_branch_types(dep))
        elif key_type == 'grandpa_pa':
            pa = self.parent(dep, type=True)
            grandpa = ''
            if pa != 'ROOT' and pa != 'root':
                grandpa = self.parent(self.parent(dep), type=True)
            key = grandpa + '/' + pa
        return key



    def phrase_store(self, phrase_def_dict, dep):
        dep_type = self.dep_types(gov, [dep])[0]
        prev_gov_info = tuple([dep_type, gov_word, gov_pos,
                              self.json_toks_text[dep-1]])
        phrase = self._phrase_info(dep)
        filesource = tuple([self.filenum, self.title, self.sent_id])
        #store in instance variable dictionary
                    #print(tuple([prev_gov_info, phrase, source]))#for debug
        if dep_type == 'ROOT' or dep_type == 'root':
            dep_type = 'sent'

        phrase_def_dict[dep_type].append(tuple([prev_gov_info,
                                                phrase,filesource]))

    #Take defaultdict(list). Store dependency loops
    #(that break tree struct and would cause infinite loops.)
    def loop_deps(self, loop_defaultdict):
        govstack=[0]
        seen_nodes = []
        loop_deps = []
        while govstack:
            gov = govstack.pop()
            seen_nodes += [gov]
            gov_word, deps_to_skip = self._word_and_chained_verbs(gov)
            dep_govs = [dep for dep in self.dep_also_govs(gov)
                        if dep not in deps_to_skip]
            #looper_deps to store
            loop_deps += [i for i in seen_nodes if i in dep_govs]

            #iterate for next nodes
            govstack += [dep for dep in dep_govs if dep not in seen_nodes]

        filesource = str(tuple([self.filenum, self.title, self.sent_id]))
        loop_defaultdict[filesource] = loop_deps





    #given gov, find potential and-verb-sequence (e.g. I ran and found and slept)
    #Return 1) words of gov/gov-verb-sequence and 
    #2)ids of and-connected verbs that shouldn't be stored in dict.
    #Return string and list of ints.
    def _word_and_chained_verbs(self, gov):
        gov_word = self.json_toks_text[gov-1]
        deps_to_skip = []
        pos = self.POS([gov])
        #if gov has POS (i.e. is not ROOT) and it is VB, 
        if (len(pos) == 1) and (pos[0][0:2] == 'VB'):
            #if gov has dep_also_govs that are verbs, and are 
            #connected to gov with conj:and, and those dep_also_govs
            #have fewer than two dependencies, add them to gov_word
            for dp in self.dep_also_govs(gov):
                if self.POS([dp])[0][0:2] == 'VB'\
                and self.dep_types(gov, [dp])[0] == 'conj:and'\
                and len(self.dep_ids(dp)) < 2:
                    gov_word += ' and ' + self.json_toks_text[dp-1]
                    deps_to_skip += [dp]
        return gov_word, deps_to_skip


    #phrase_info given gov. (helper for phrase_collect_and_store)
    #in format [(dep_type, dependent, POS of dependent, lemma) ...]
    #sorted by word order in the sentence.
    #Return list of tuples with (str, str, str, str)
    def _phrase_info(self, gov):
        operator = __import__('operator')
        outlist = []
        #list dependents, dep types, and governor with type 'gov'
        id_types = self.dep_id_types(gov) + [(gov, 'gov')]
        #sort into readable word order in original sentence
        id_types.sort(key = operator.itemgetter(0))
        #find POS for each
        for id_type in id_types:
            id, type = id_type
            #mark branch status (root, branch, leaf)
            if type == 'gov':
                branch_status = 'root'
            elif id in self.dep_also_govs(gov):
                branch_status = 'branch'
            else:
                branch_status = 'leaf'
            outlist += [(self.json_toks_text[id-1], type,
                         self.json_toks[id-1]['pos'],
                         self.json_toks[id-1]['lemma'],
                         branch_status)]
        return outlist


    def Tree_id(self):
        return (self.title, self.filenum, str(self.sent_id))



    '''given Tree_id, branch info extraction (phrase parsing formalized
    into branch structure.)'''
    #def branch_id(self, dep_gov):
    #    return 1

    def parent(self, dep, type = False):
        #NOTE: if parser erroneously only marked the first occurrence,
        #e.g. with Austen-Pride file 33 sent 3, then it would be
        #safer to take the [-1] of find() instead of next()
        id, tp = next((dep_token['governor'], dep_token['dep'])
                        for dep_token in self.json_deps
                        if dep_token['dependent'] == dep)
        if type:
            return tp
        else:
            return id


    def branch_parent_path(self, dep_gov):
        path = [dep_gov]
        while dep_gov != 0:
            parent = self.parent(dep_gov)
            if 'parent' in locals():
                path += [parent]
                dep_gov = parent
            else:
                print("Tree: ", Tree_id(), " dep_gov: ",  dep_gov, 
                      "branch_parent_path didn't find parent")
                break
        path.reverse()
        return path


    #expect branch_def_dict = defaultdict(list). 
    #Plan is to use this as a pointer, with sufficient
    #identifiers when I'm trying to find which branches could fill a blank.
    def branch_info_store(self, branch_def_dict, branch_id):
        branch_def_dict['branch_id'] = branch_id
        branch_def_dict['tree_id'] = self.Tree_id()
        branch_def_dict['tree_branch_id'] = ('_'.join(self.Tree_id())
                                             + '_' + str(branch_id))
        branch_def_dict['hc_type'] = self.branch_hctype(branch_id)
        #branch_def_dict['parent_dep'] = self.parent(branch_id, type=True)
        #parent_path = self.branch_parent_path(branch_id)
        #branch_def_dict['parent_path'] =[parent_path,self.text(parent_path)]

        #dep_chain = self.dep_chain(branch_id)
        #dep_chain_types = self.dep_chain(branch_id, types_only=True)
        #branch_def_dict['children'] = [self.dep_id_types(branch_id),
        #                      self.text(self.dep_ids(branch_id))]
        #branch_def_dict['children_path'] = [dep_chain,dep_chain_types,
        #                                   self.text(dep_chain)]
        #branch_def_dict['self_leaves'] = self.branch_with_leaves(branch_id,
        #                                                         text=True)
        #branch_def_dict['self_leaves_branches'] = self.branch_leaf_text_branch_type(branch_id)
        #branch_def_dict['branches'] = self.branch_branch_types(branch_id)
        #branch_def_dict['grandpa'] = self.branch_grandpa(branch_id)

        '''7/21/16 branch_fetch functions'''
        branch_def_dict['branch_slots'] = self.branch_slots(branch_id)
        branch_def_dict['own_branches'] = self.dep_also_govs(branch_id)
        branch_def_dict['branch_keys'] = self.branch_keys(branch_id)


    def branch_with_leaves(self, branch_id, text=False):
        out = [dep_id for dep_id in self.dep_ids(branch_id)
                       if dep_id not in self.dep_also_govs(branch_id)]
        out += [branch_id]
        out.sort()
        if text:
            out = self.text(out)
        return out


    #NOTE: QUICK AND DIRTY SLOW IMPLEMENTATION
    def branch_leaf_text_branch_type(self, branch_id):
        out = []
        also_govs = self.dep_also_govs(branch_id)
        for tok in self.dep_ids(branch_id):
            if tok in also_govs:
                out.append(self.parent(tok, type=True))
            else:
                out += self.text([tok])
        return out
    

    def branch_leaf_types(self, branch_id):
        return [dep_type for dep_id, dep_type
                          in self.dep_id_types(branch_id)
                          if dep_id not in self.dep_also_govs(branch_id)]

    def branch_child_types(self, branch_id):
        return [dep_type for dep_id, dep_type
                          in self.dep_id_types(branch_id)]

    def branch_branch_types(self, branch_id):
        return [dep_type for dep_id, dep_type
                          in self.dep_id_types(branch_id)
                          if dep_id in self.dep_also_govs(branch_id)]

    def branch_grandpa(self, branch_id):
        pa = self.parent(branch_id, type=True)
        grandpa = ''
        if pa != 'ROOT' and pa != 'root':
            grandpa = self.parent(self.parent(branch_id), type=True)
        return grandpa 

    '''fetch_branch functions as specified on paper 7/21/16 '''
    def branch_slots(self, branch_id):
        out = []
        also_govs = self.dep_also_govs(branch_id)
        branch_and_deps = self.dep_ids(branch_id)
        branch_and_deps += [branch_id]
        branch_and_deps = sorted(branch_and_deps)
        for tok in branch_and_deps:
            if tok in also_govs:
                out.append([])
            else:
                out += self.text([tok])
        return out

    def branch_hctype(self, branch_id):
        return (self.parent(branch_id,type=True)
                    + '/' + '/'.join(self.branch_child_types(branch_id)))

    def branch_keys(self, branch_id):
        return [self.branch_hctype(child_branch_id) for child_branch_id 
                in self.dep_also_govs(branch_id)]

    ###NOTE:7/25
    #while grafting, check for types of incoming branch's hctype. 
    #try the possibility of dropping nmod or ccomp. 

    '''
    access phrases
    '''

    """given a sentence and a governor
    functions to find and parse dependency chains
    NOTE: these don't seem to be used at all in parsing.
    """
    #chain of dependencies, recursively reach into the dependencies of any
    #also_gov dependencies. NOTE: the governor appears at the beginning of (each
    #nested) list
    def dep_chain(self, gov, seen_nodes = [], types_only=False):
        seen_nodes = [gov]
        if gov != 0 and types_only:
            chain=[self.parent(gov, type=True)]
        else:
            chain = [gov]
        deps_to_skip = []
        also_govs = [dep_g for dep_g in self.dep_also_govs(gov) 
                         if dep_g not in deps_to_skip
                         and dep_g not in seen_nodes]
        also_govs = list(set(also_govs))    #remove double-references, 
                                            #such as Austen-Pride 33, 3
        for dep_id, dep_type in self.dep_id_types(gov):
            if dep_id in also_govs:
                chain += [self.dep_chain(dep_id, seen_nodes, types_only)]
            else:
                if types_only:
                    chain += [dep_type]
                else:
                    chain += [dep_id]
        return chain



#    #for dep_chain
#    #return element at the end of path
#    def nest_list_ele(nest_list, path_list):
#        #travel lists until reach the wanted position. 
#        for i in range(path_list):
#            ele = nest_list[path_list[i]]    #path_list[i] is next_index
#        return ele
#
#    #replace element at the end of path with given ele
#    def nest_list_replace(nest_list, path_list, ele):
#        for 

    #from dep_chain, extract sub_phrases. I.e., cut out nonlists
    #interpret a "sub_phrase" as a dep_also_gov
    #returns list of lists. NOTE: return the original gov at the head.
    def get_sub_phrases(self, nest_list):
        return [[nest_list[0]]] + [ele for ele in nest_list if isinstance(ele, list)]

    #from dep_chain, remove phrases. (see interpretation of "sub_phrase" in
    #description of function get_sub_phrases.
    def remove_sub_phrases(self, nest_list):
         return [ele for ele in nest_list if not isinstance(ele, list)]




#after small changes when developing:
#from importlib import reload as r
#r(j)
