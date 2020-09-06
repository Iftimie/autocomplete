# Step by step: Autocomplete System. 

Inspired from [here](https://lopespm.github.io/2020/08/03/implementation-autocomplete-system-design.html)

In this version there are two major changes. Instead of using shared volumes and local paths, now the file sharing is done
using HDFS. Also instead of writing new phrases to files, a message broker is introduced. The message broker has a sink
(kafka-connect) and it dumps the files into timestamp named folders which contain avro files.


To start the project run:

`make run`

In a new terminal run:

`make setup`

To populate with phrases run:

`make populate_search`

To start the trie building, run:

`make do_tasks`