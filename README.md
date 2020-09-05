# Step by step: Autocomplete System. 

Inspired from [here](https://lopespm.github.io/2020/08/03/implementation-autocomplete-system-design.html)

One way to solve the previous problem, when the distributor was listing the directory every time, is to send a post 
request from the triebuilder to distributor/backend to reload the trie.

Thus the information flow so far is:
- collect-phrase in assembler collector
- newphrase is appended to its current sliding window
  - if newphrase is in a new sliding window then:
     - request is sent to triebuilder to build the trie that includes the previous sliding window
     - after triebuilder builds the new trie, a request is sent to distributor.backend to load the new trie

To start the project run:

`sudo docker-compose up`