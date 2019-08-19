import torch
from pytorch_transformers import BertTokenizer
from pytorch_transformers import BertModel
from torch.nn.utils.rnn import pad_sequence

from charities import load_all_charities
from utils import batch


BERT_MODEL_VERSION = 'bert-base-uncased'
EMBEDDINGS_BATCH_SIZE = 10


tokenizer = BertTokenizer.from_pretrained(BERT_MODEL_VERSION)
model = BertModel.from_pretrained(BERT_MODEL_VERSION)
model.eval()


def get_embeddings(documents):
    all_embeddings = [
        _get_embeddings(doc_batch)
        for doc_batch in batch(documents, EMBEDDINGS_BATCH_SIZE)
    ]

    return torch.cat(
        all_embeddings,
        dim=0,
    )


def _get_embeddings(documents):
    all_indexed_tokens = []

    for text in documents:
        tokenized_text = (
            [tokenizer.cls_token] +
            tokenizer.tokenize(text) +
            [tokenizer.sep_token]
        )

        indexed_tokens = tokenizer.convert_tokens_to_ids(tokenized_text)
        all_indexed_tokens.append(torch.tensor(indexed_tokens))

    tokens_tensor = pad_sequence(all_indexed_tokens, batch_first=True)
    attention_mask = torch.where(
        tokens_tensor != 0,
        torch.ones(tokens_tensor.shape),
        torch.zeros(tokens_tensor.shape),
    )

    hidden_states, _ = model(
        tokens_tensor,
        attention_mask=attention_mask,
    )

    return hidden_states.permute(1, 0, 2).sum(axis=0)


charities = load_all_charities()
charity_vectors = get_embeddings(charities['description'].tolist())


def search_charities(query, top_n=5):
    [query_vector] = get_embeddings([query])
    distances = torch.norm(
        charity_vectors - query_vector,
        p=2,
        dim=1,
    )

    best_match_indices = torch.argsort(distances)[:top_n]

    return charities.iloc[best_match_indices]
