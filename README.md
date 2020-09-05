# Step by step: Autocomplete System. 

Inspired from [here](https://lopespm.github.io/2020/08/03/implementation-autocomplete-system-design.html)

Most basic start. There are routes for:
- static files
- search
- top-phrases
- index

To run the project, run the following commands:

`sudo pip3 install -r requirements.txt`

Then start the application with:

`sudo gunicorn3 -b 0.0.0.0:80 main:app --reload`

This initial implementation is simple stupid. Everything is grouped into a monolith and it is very inneficient and unreliable.

Every time a top-phrases is requested, the app reads the trie from disk, and then computes the results for a prefix.

Every time a search is requested, the app constructs a new trie and saves it to disk.
