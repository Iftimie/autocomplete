# Step by step: Autocomplete System. 

Inspired from [here](https://lopespm.github.io/2020/08/03/implementation-autocomplete-system-design.html)

In this newer version, the distributor backend lists the shared directory during each requests to see if there are new
 tries. It will load the new trie only if there is a new file. Each file is named after the timestamp of its creation.
 The directory listing is still inefficient, but better than loading the file every time.

To start the project run:

`sudo docker-compose up`