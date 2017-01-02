#Pauli Xu 7/15/16 v0.2. assume branch takes a key,and a list of def_dicts. 

#NOTE: key_type and item_type have to "agree" between 
        #d.py, build_chain_dict.py, and j.py. (there will be files stored, 
        #so something will be read. But when deving, know which file
        #you want to read.


#phrase_dict.py (d.py)  (later modify module)
#For input, take a json file that stores a
#phrase_dict, in the format specified in "classes/j.py" (json_parses.py)


'''initialization steps for development'''
#gather dict_jsons titles from given dict_jsons folder.

from collections import defaultdict

def gather_titles(folder):
    import glob
    titles = []
    for longfilename in glob.iglob(folder + '/' + '*'):
        #pick last filename, ignore paths
        filename = longfilename.split('/')[-1]
        title = filename.split('_')[0]
        titles.append(title)
    #remove duplicates
    return list(set(titles))

#read json into dictionary
def load_dict(title, folder, item_type, key_type):
    import json
    filename = folder + "/" + title + '_' +\
            item_type + '_' + key_type + ".dict.json"
    f = open(filename,'r')
    json_string = f.read()
    f.close
    print("loaded dict:", filename)
    return json.loads(json_string)

#use dict2 keys to concatenate dict2 lists into def_dict1 lists
def dict_list_concat(def_dict1, dict2):
    for key in dict2.keys():
        def_dict1[key] += dict2[key]


#execute load dict.

folder = "dict_jsons"
titles = gather_titles(folder)
item_type = 'branch'        #currently accepts 'branch' and 'phrase'
key_types = ['hctype', 'tree_branch_id']
print("dict_key:", key_types)


dict_hctype = defaultdict(list)
dict_tree_branch = defaultdict(list)
for title in titles:
    dict_hctype_to_append =load_dict(title, folder, item_type, key_types[0])
    dict_tree_branch_to_append = load_dict(title, folder, 
                                           item_type, key_types[1])
    dict_list_concat(dict_hctype, dict_hctype_to_append)
    dict_list_concat(dict_tree_branch, dict_tree_branch_to_append)

#dict_branches = load_dict(title, folder, item_type, key_types[2], chunks)
#dict_grandpa_pa= load_dict(title, folder, item_type, key_types[3], chunks)
 




'''helper functions, mainly before branch_dict 7/14'''



'''helper for hctype dict, 7/18'''
def keys_with_child(head):
    return [key for key in phrase_dict_hctype.keys()
            if key.find(head) != -1]

'''helper for head dict, 7/18'''
def keys_for_grandpa_pa(branch_dict_entry):
    pa = branch_dict_entry['parent_dep']
    children = branch_dict_entry['branches']
    return [pa + child for child in children]


#give readable index names to accessing the info tuples in the dict values. 
header_tup_ind, phrase_tup_ls_ind, source_tup_ind = 0, 1, 2



'''categorizing dependencies/branches
'''
#list of dependencies that (atleast once) appear as branches/nodes/phrases 
#with further deps
#node_ls = phrase_dict.keys()


#NOTE: Should count how often a dependency appears as a leaf vs. as a branch


#NOTE: list dependencies that feel more tightly bound to the phrase
    #call them buds. E.g. nsubj, dobj.
    #xcomp expanded

#NOTE: classify clauses, esp. advcl. Maybe by their first word? 
    #(when, for,...)
    #for clauses, the headers matter a lot
from collections import defaultdict
def dep_by_starter_dict(dep):
    starter_dict = defaultdict(list)
    for i, tup in enumerate(phrase_dict[dep]):
        #for key, get phrase_tup -> word_tup -> then word
        starter_dict[tup[1][0][0]] = (tup, "dep_id is " + str(i))
    return starter_dict

    ##for advcl:
    #when, while, first, gerund (running), whilst, often, (time signifiers)
    #place


'''accessing phrase dictionary
'''

#terminology: 
    #phrase_tup_ls is a list of "triples" of "tuples"/lists
        #[[(phrase1 head tup), phrase1_tup, (phrase1 source tup)]
        # [(phrase2 head tup), phrase2_tup, ...]
        #see phrase_tup below
    #phrase_tup is a list of lists. 
        #[[word1 "tuple"], [word2 "tuple"], ...]
    #word_tup is a list
        #[word1 "tuple"]
    #word_alph is alphabetically spelled word

    #in general, plural means a list. E.g. phrases means list of phrases

#given a phrase type (e.g. 'advcl' or 'sent') and a num (e.g. 2nd entry
#in the category) return the list of tuples of words in the phrase.
    #if find problem case, use get_problem_sent() 
def get_phrase_tups (phrase_type, as_leaves=False):
    if not as_leaves:
        phrase_tups = [phrase_tup_ls[1]
                       for phrase_tup_ls in phrase_dict[phrase_type]]
    else:
        phrase_tups = [leafize_phrase_tup(phrase_tup_ls[1])
                       for phrase_tup_ls in phrase_dict[phrase_type]]
    return phrase_tups

def get_phrases_as_word_alphs (phrase_type):
    #word_tup[0] is the spelled out word
    return [([word_tup[0] for word_tup in word_tups], i)
            for i,word_tups in enumerate(get_phrase_tups(phrase_type))]


#return how many items exist for the dependency type.
#return a list of pairs (num of items in the type, type)
def lens_types(phrase_dict):
    lens_types = [(len(phrase_dict[type]), type) for type in phrase_dict.keys()]
    lens_types.sort(key=lambda tup: tup[0])
    return lens_types




'''inspecting leaf/branch relations
'''

###pretty prints/lists


#def show_buds_and_branchroots

def show_leaf_branch(phrase_tup):
    out = []
    for word_tup in phrase_tup:
        #check if dep_type is a node type
        if word_tup[1] in node_ls:
            out += [word_tup[1]]
        else:
            out += [word_tup[0]]
    return out




#remove branches from phrase_tup
def leafize_phrase_tup(phrase_tup):
    branch_status_ind= -1
    return [word_tup for word_tup in phrase_tup
                    if word_tup[branch_status_ind] != 'branch']

#remove branches from phrase_tup_ls
def leafize_phrase_tup_ls(phrase_tup_ls):
    header = 0; source = 2
    phrase_tup = phrase_tup_ls[phrase]
    out = []
    out.append(phrase_tup_ls[header])
    out.append(leafize_phrase_tup(phrase_tup))
    out.append(phrase_tup_ls[source])
    return out

#NOTE: study which of the key types intro new clauses, which modify 
    #the sentence/head "more simply"




#sprouting

#trial 1: printing with replaced branches. (with phrases)
import random
def sprout_rand(phrase_tup):
    out = []
    sources = []
    for word_tup in phrase_tup:
        branch_status = -1; dep = 1
        if word_tup[branch_status] == 'branch':
            dep_type = word_tup[dep]
            rand_int = random.randint(0, len(phrase_dict[dep_type]))
            rand_phrase_tup = phrase_dict[dep_type][rand_int]
            out.append(rand_phrase_tup[1])
            sources.append((rand_phrase_tup, rand_int))
        else:
            out.append(word_tup)
    return out, sources


'''trial 2, for branches. Pseudo code:
    #

    #goal meth1: branch sequence, with markings of branch insertions. (would need two
    lists)
    #goal meth2: branch functions/ branch-tuples. each branch would know how
    many branch holes it has. It needs that many branch_ids as inputs. a
    special id '-' marks that the branch retains what it had at the hole. I
    would begin with a top branch and fill holes. Each branch is a (nested)
    tuple. So this is a lambda construct. I would return a decent-sized nested
    list.


        #goal: text printout.
'''







#quick and dirty sprouting method based on hc_type
#return list of child_branches. 
def branch_hc(branch_dict_entry):
    child_branches = []
    for ele in branch_dict_entry['children_path'][1]:
        if isinstance(ele, list):
            child_branches.append(ele)
    return child_branches

def direct_children(nest_ls):
    out = []
    for ele in nest_ls:
        if isinstance(ele, list):
            out.append(ele[0])
        else:
            out.append(ele)
    return out


def flatten(nest_ls):
    out = []
    for ele in nest_ls:
        if not isinstance(ele, list):
            out.append(ele)
        else:
            out += flatten(ele)
    return out




#find branch_hc of a child. Find a replacement at random from hc_type dict
def sprout_hc(branch_dict_entry, sprout_child_order):
    child = direct_children(branch_hc(branch_dict_entry)[sprout_child_order])
    child = ''.join(child)
    

#have a graft function - take a sentence with a whole branch within it. 
#remove the branch (with all its dependencies). Sprout a new branch.






#inspecting phrases
from classes.j import json_parser

#e.g.
#dep = 'nsubj'
#problem = 2306
#def get_problem_sent(dep, problem_id):
#    prob_phrase = phrase_dict[dep][problem_id]
#    print("phrase: \n", prob_phrase)
#    prob_filenum = prob_phrase[2][0]
#    prob_title = prob_phrase[2][1]
#    prob_sent_id = prob_phrase[2][2]
#
#    j = json_parser(prob_title, prob_filenum)
#    j.update_sent_inst_variables(prob_sent_id)
#    print("\nproblem sentence:\n", j.json_toks_text)
#    return j

#take tree_id list of the form [title, filenum, sent_id]
    #and branch_id of the form int.
#e.g. ['Austen-Pride', '348', '3'], 13
#return instance of the problem sentence. 

def get_problem_sent(branch_dict_entry, branch = False):
    try:
        tree_id = branch_dict_entry['tree_id']
    except:
        #remove last element of tree_branch_id
        tree_id = branch_dict_entry['tree_branch_id'].split('_')[:-1]
    print(tree_id)
    j = json_parser(tree_id[0], tree_id[1])
    j.update_sent_inst_variables(int(tree_id[2]))
    if branch ==True:
        branch_id = branch_dict_entry['branch_id']
        print("\nproblem phrase:\n", j.text(j.dep_chain(branch_id)))
    print("\nproblem sentence:\n", j.json_toks_text)
    return j




'''7/25/16: 
branch_fetch functions, as designed on paper on 7/21/16'''

import random


def form_tree_branch_id(tree_id, branch_id):
    return '_'.join(tree_id) + '_' + str(branch_id)

def tree_branch_to_hctype(tree_branch_id):
    return dict_tree_branch[tree_branch_id][0]['hc_type']

def tree_branch_path_hctypes(mod_tree):
    path_hctypes = []
    for tree_branch in mod_tree['tree_branch_path']:
        if not tree_branch: #check against []
            path_hctypes.append(tree_branch)
        else:
            path_hctypes.append(tree_branch_to_hctype(tree_branch))
    return path_hctypes

#helper for expand(). basic fetch_function, just return the
#stuff with the given tree_branch_id.

def fetch_own(tree_branch_id):
    #below, dict_tree_branch has [0] because dict_tree_branch is collected
    #as a list of dictionaries, even though only entry is expected.
    branch_dict_entry = dict_tree_branch[tree_branch_id][0]
    tree_branch_id = branch_dict_entry['tree_branch_id']
    branch_slots = branch_dict_entry['branch_slots']
    tree_id = branch_dict_entry['tree_id']
    branch_list = [form_tree_branch_id(tree_id, own_branch)
                   for own_branch in branch_dict_entry['own_branches']]
    return tree_branch_id, branch_slots, branch_list

#find random tree_branch that shares the hc_type with given tree_branch
def fetch_random_hctype(tree_branch_id):
    hctype = dict_tree_branch[tree_branch_id][0]['hc_type']
    options = len(dict_hctype[hctype])
    choice = random.randint(0, options-1)
    print('#options: ', options)
    rand_t_b_id = dict_hctype[hctype][choice]['tree_branch_id']
    return fetch_own(rand_t_b_id)



#helper for expand(). convert a branch_dict_entry into mod_tree
def form_mod_tree(branch_dict_entry):
    tree_branch_id = branch_dict_entry['tree_branch_id']
    mod_tree = {}
    mod_tree['tree_branch_id'], mod_tree['branch_slots'], \
            mod_tree['branch_list'] = fetch_own(tree_branch_id)
    mod_tree['tree_branch_path'] = [tree_branch_id]
    return mod_tree

def expand_mod_tree(mod_tree, fetch_function):
    #check for empty branch_list (no branching slots)
    if not mod_tree['branch_list']:
        print('empty branch list, return as is')
        return mod_tree
    out_mod_tree = {}
    out_mod_tree['branch_slots'] = []
    out_mod_tree['branch_list'] = []
    out_mod_tree['tree_branch_path'] = mod_tree['tree_branch_path']
    branch_list_pos = -1
    for ele in mod_tree['branch_slots']:
        if not isinstance(ele, list):
            out_mod_tree['branch_slots'].append(ele)
        else:
            branch_list_pos += 1
            try: 
                child_tree_branch_id = mod_tree['branch_list'][branch_list_pos]
            except:
                print('error branch-list_pos went over\n',
                       'printing mod_tree, out_mod_tree, branch_list_pos')
                return mod_tree, out_mod_tree, branch_list_pos
            t_b_id, b_slots, b_list = fetch_function(child_tree_branch_id)
            #change b_slots to append if want to see where they come in
            out_mod_tree['branch_slots'] += b_slots
            if b_list:  #check if not empty
                out_mod_tree['branch_list'] += b_list
            #a marker for child expansion
            out_mod_tree['tree_branch_path'].append([])
            out_mod_tree['tree_branch_path'].append(t_b_id)
    #a marker for end of a layer expansion
    out_mod_tree['tree_branch_path'].append([])
    #####NOTE: while exploring, tree_branch_path is tacky
    #out_mod_tree['tree_branch_path'] = ['ignored']
    return out_mod_tree


def expand_mod_tree_through(mod_tree, fetch_function):
    #do...until. (check for case with no branch_slots)
    mod_tree = expand_mod_tree(mod_tree, fetch_function)
    while mod_tree['branch_list']:
        mod_tree = expand_mod_tree(mod_tree, fetch_function)
    return mod_tree


#give random mod_tree
def get_random_mod_tree():
    keys = list(dict_tree_branch.keys())
    options = len(keys)
    choice = random.randint(0, options-1)
    rand_key = keys[choice]

    branch_dict_entry = dict_tree_branch[rand_key][0]
    return form_mod_tree(branch_dict_entry)




print("""
    ###################################################
      Test with the following commands:

    ###load a tree
x = d.get_random_mod_tree()

    #show tree
x

    #show dict keys for each child branch 
    #(marked as [] in 'branch_slots')
d.tree_branch_path_hctypes(x)

    ###expand the child branches once
    #(branches of children are left unexpanded)
x = d.expand_mod_tree(x, d.fetch_random_hctype)

    #show expanded tree
x

    #show dict keys for child branches
d.tree_branch_path_hctypes(x)

    ####################

    ###Or expand the tree and its children
    #there are no more branches to expand:
x = d.get_random_mod_tree()

d.expand_mod_tree_through(x, d.fetch_random_hctype)

    ####################

    ###See the original sentence
    #and gain access to the json parse
    #(for now, use only on unexpanded tree)
j = d.get_problem_sent(x)

    #see some dependency ids and texts based on Stanford dependency parse
j.dep_chain(0)

j.text(j.dep_ids(0))
      ######################################################
      """)
