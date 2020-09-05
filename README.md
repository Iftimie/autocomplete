# Step by step: Autocomplete System. 

Inspired from [here](https://lopespm.github.io/2020/08/03/implementation-autocomplete-system-design.html)

This newer version simply has a new service (assembler.triebuilder) that builds the trie when it is commanded to.

The command to build the trie comes from assembler.collector when a new phrase is part of a new 30 minute sliding window.
It will make a request to the triebuilder /build_trie endpoint.

The triebuilder will receive the name of the previous sliding window, but for no special reason it will rebuild the tree
from all available files. 

To start the project run:

`sudo docker-compose up`