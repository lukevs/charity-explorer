# YouCharity

Intelligent charity search backed by BERT and Pytorch.

Our model implements a document search using hugging-face's pytorch-transformers implementation of BERT.

Like other implementations of BERT for search (ex: https://arxiv.org/abs/1901.04085), we use a two step process:
- A fast search for candidate results
- A slower but more accurate ranking step

Unlike other methods, we leverage BERT for both steps, instead of just the second step.

Candidate results
-----------------

To find candidate results, we split documents into sentences and run each through BERT.

To compute sentence representations, we mean pool the _earliest_ layer of BERT. We found using the earliest layer performed best in returning results because it encodes more word level than sentence level semantics, which is more similar to the structure of queries.

Sentence encodings are precomputed and saved. The server loads these embeddings on startup.

Incoming queries are encoded with the same method as each sentence and are compared against sentence vectors using cosine similarity.

We average the most similar N=20 sentences for each document to get a similarity score for the document.

Ranking
-------

To further improve results, we put the top candidate results through a ranking step.

The query string is concatenated with the full description for each document (using BERT's 2 sentence CLS-SEP-SEP encoding). The concatenated string is passed through a BERT model with a pretrained next sentence prediction classifier on top. The outputs of the classifier are then used to rank these most similar documents, returning the top ranked documents as results of the search.

## Running the web site

From the `/web` folder, run the following commands:

<pre>
  yarn
  yarn start
</pre>

The website should now be running on port 3000.

## Running the server

* Create a new virtualenv
* Activate it

<pre>
  pip install -r requirements.txt`
</pre>

* Run with `python app.py`

#### Search API

**Request**
```
POST localhost:8778/search
{
  "query": "I want a dog"
}
```

**Response**
```
{
  "results": [
    {
      "name": "Dog charity",
      "description": "Best dog charity in town"
    },
    ...
  ]
}
```
