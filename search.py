import torch
from pytorch_transformers import BertTokenizer
from pytorch_transformers import BertForNextSentencePrediction
from torch.nn.utils.rnn import pad_sequence

from charities import load_all_charities


BERT_MODEL_VERSION = 'bert-base-uncased'


charities = load_all_charities()
tokenizer = BertTokenizer.from_pretrained(BERT_MODEL_VERSION)
model = BertForNextSentencePrediction.from_pretrained(BERT_MODEL_VERSION)
model.eval()


def predict_next_sentence_probabilities(query, documents):
    all_indexed_tokens = []
    all_segments_ids = []

    with torch.no_grad():
        tokenized_query = (
            [tokenizer.cls_token] +
            tokenizer.tokenize(query) +
            [tokenizer.sep_token]
        )

        for document_sentence in documents:
            tokenzied_document = (
                tokenizer.tokenize(document_sentence) +
                [tokenizer.sep_token]
            )

            indexed_tokens = tokenizer.convert_tokens_to_ids(
                tokenized_query + tokenzied_document,
            )

            segments_ids = (
                [0] * len(tokenized_query) +
                [1] * len(tokenzied_document)
            )

            all_indexed_tokens.append(torch.tensor(indexed_tokens))
            all_segments_ids.append(torch.tensor(segments_ids))

        tokens_tensor = pad_sequence(
            all_indexed_tokens,
            batch_first=True,
        )

        segments_tensors = pad_sequence(
            all_segments_ids,
            batch_first=True,
        )

        predictions = model(
            tokens_tensor,
            segments_tensors,
        )[0]

        prob_scores = torch.nn.functional.softmax(
            predictions,
            dim=1,
        )[:, 0]

        return prob_scores


def search_charities(query, top_n=5):
    descriptions = charities['description'].tolist()
    probs = predict_next_sentence_probabilities(
        query,
        descriptions,
    )

    best_match_indices = torch.argsort(probs).numpy()[::-1][:top_n]

    return charities.iloc[best_match_indices]
