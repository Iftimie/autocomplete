# Step by step: Autocomplete System. 

Inspired from [here](https://lopespm.github.io/2020/08/03/implementation-autocomplete-system-design.html)

The previous version was communicating information by defining http endpoints. In this version, the commmunication of 
events such as trie loading is done by using Zookeeper. 

Another change is that the signalling from assembler.collector to assembler.triebuilder was removed. The job of building
a trie is triggered by the script tasks/do_tasks.sh as in the [original implementation](https://lopespm.github.io/2020/08/03/implementation-autocomplete-system-design.html). 
This change will also come in handy when the message broker will be introduced.

The script looks at the last 3 files that contain phrases, creates a new directory, copies the files in the new directory
and runs  Zookeeper CLI in order to notify the assembler.triebuilder. It is important to mention that the triebuilder is no longer
a service defined with falcon API.

After the trie is built, assembler.triebuilder the distributor.backend that it should reload the trie. 
The notification is done again with Zookeeper.

To start the project run:

`make run`

In a new terminal run:

`make setup`

After a few phrases have been introduced and a few files can be seen in shared/shared_phrases, run:

`make do_tasks`