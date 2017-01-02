# Phraser

This project explores what parts of an English sentence can be swapped with parts of another sentence without breaking syntax. For example, with the sentence "Mary needed a pen to complete her exam," the word 'pen' could be swapped with 'car,' or the phrase 'needed a pen' could be swapped with 'moved abroad.' 

The larger aim is to generate "stylistic" sentences: given large lists of syntactically correct phrases, we may filter them by meaning and sound.

The code implements three tasks: 

1) Cleaning a text and parsing it with Stanford CoreNLP Dependency Parser. 
2) Organizing the parses into dictionaries of trees and branches (with different keys and pointers to original texts)
3) Accessing trees and swapping branches (according to dictionary keys)


The current commit includes ready parses of several novels by Jane Austen. The tasks above are detailed in reverse order:

### 3) Accessing trees and swapping branches

In python3, import d. 
Importing the code will print out further directions. 


Sample output:

```python
>>> import d
# loading branch dictionaries
dict_key: ['hctype', 'tree_branch_id']
loaded dict: dict_jsons/Austen-Emma_branch_hctype.dict.json
loaded dict: dict_jsons/Austen-Emma_branch_tree_branch_id.dict.json
loaded dict: dict_jsons/Austen-Pride_branch_hctype.dict.json
loaded dict: dict_jsons/Austen-Pride_branch_tree_branch_id.dict.json

#load a tree
>>> x = d.get_random_mod_tree()

#show tree. 
>>> x
{'branch_list': ['Austen-Pride_1025_3_3', 'Austen-Pride_1025_3_7', 'Austen-Pride_1025_3_18'], 'tree_branch_path': ['Austen-Pride_1025_3_11'], 'branch_slots': ['And', [], ',', [], ',', 'find', 'them', 'out', ',', [], '.'], 'tree_branch_id': 'Austen-Pride_1025_3_11'}

#show branch keys
>>> d.tree_branch_path_hctypes(x)
['ROOT/cc/ccomp/punct/advcl/punct/dobj/compound:prt/punct/advcl/punct']


>>> x = d.expand_mod_tree(x, d.fetch_random_hctype)
#options:  14
#options:  24
#options:  19
>>> x
{'branch_list': ['Austen-Pride_427_0_23'], 'tree_branch_path': ['Austen-Pride_1025_3_11', [], 'Austen-Mansfield_427_0_16', [], 'Austen-Pride_427_0_21', [], 'Austen-Emma_1586_1_5', []], 'branch_slots': ['And', 'complaining', 'about', ',', 'when', 'Charles', 'gets', [], ',', 'find', 'them', 'out', ',', 'when', 'she', 'did', 'speak', '.']}
>>> d.tree_branch_path_hctypes(x)
['ROOT/cc/ccomp/punct/advcl/punct/dobj/compound:prt/punct/advcl/punct', [], 'ccomp/advmod', [], 'advcl/advmod/nsubj/nmod:to', [], 'advcl/advmod/nsubj/aux', []]
```

### 2) Organizing the parses into dictionaries of trees and branches

from commandline, execute
python3 build_chain_dict


The current keys are "hctypes", which is a naive concatenation of
the parent of the current branch and all of its child dependencies.


### 1) Cleaning a text and parsing it with Stanford CoreNLP Dependency Parser
1) Download Stanford CoreNLP Dependency Parser (search online)
2) store your text file in the folder "texts." NOTE: The text goes through a simple cleanup process that removes some newlines ('\n') and periods (e.g. "Mr."), since these confuse the parser. However, introduction texts and licence information is not cleaned. 
3) use a text editor to open "txtclean_Austen.py"
4) update variable "nlp_executable" with the path to the folder that contains Stnaford CoreNLP
5) update variable "titles" with the name of your text file.
