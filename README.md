# YouCharity

Intelligent charity search backed by BERT and Pytorch.

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
