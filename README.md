# charity-explorer

## Getting started

Create a new virtualenv

Activate it

`pip install -r requirements.txt`

run with `python app.py`

## Search

**Request**
`POST localhost:8778/search`
```
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
