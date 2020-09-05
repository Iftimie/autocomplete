# Step by step: Autocomplete System. 

Inspired from [here](https://lopespm.github.io/2020/08/03/implementation-autocomplete-system-design.html)

This improved version has the original the main.py split into 3 parts:
- gateway
  - contains the html, css and javascript files
- assembler/colletor
  - collects new phrases and immediately constructs the trie every time (still inefficient)
- distributor/backend
  - generates results based on prefix (still loads the trie from disk everytime)

The 3 components are organized into docker containers.

To start the project run:

`sudo docker-compose up`