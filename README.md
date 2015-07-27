# Topic-Modeling
Topic Modeling to improve libraries search

SYNOPSIS:

The Project aims at improving the search preformed in the united library through the use of Topic Modeling Algorithms, specifially
The Latent Dirichlet allocation (LDA).Topic Modeling is a statistical model that is used to discover the abstract topics that 
occur in a collection of documents. We show how the use of these topics(A collection of words that has a high chance of appearing
together) in our search can result in better results that using keywords.
Our input was the metadata of books received from the united library Catalog in Israel in Marc Format.

CODE:

1- createJsonMarc.py: Runing on our Marc data and creating a Json type file for each book that includes its metadata       Duplicates were solved and the needed parsing was performed.

2- JsonParser.py: Each json file(book) was converted to a text file. This text file includes only the metadata that will help us during our search. For instance, title, subjects and comments for that book. This data was parsed (regex) in order to     get the data in the correct form. This was performed on 870000+ English books as well as some hebrew books. 
These files were used to create the topics.(Topic Modeling) (LDA Algorithm)

Mallet for English topics  http://mallet.cs.umass.edu/

LemLDA for hebrew topics   http://www.cs.bgu.ac.il/~nlpproj/LDAforHebrew.html
   
3- DataLoad.py: Both our data (Json files with all the metadata for each book) and the results obtained through runing the LDA algorithm are added to our database.

4- MakeWordClouds.py: Using the data stored in the database, and performing other calculations to determine that weight of each word in a topic, a word cloud is being created for each topic that includes its words sized to fir their weight. This is used as a visualization technique.

5- searchInterface.py: Our Search Interface. The user enters the word he would like to search for,and recieves the first 2 word clouds(topics) that relate to that word. Clicking the word cloud will retrieve the book names related to it.

MANUALS
