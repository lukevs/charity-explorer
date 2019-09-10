import torch
from pytorch_transformers import BertTokenizer
from pytorch_transformers import BertModel
from torch.nn.utils.rnn import pad_sequence


BERT_MODEL_VERSION = 'bert-base-uncased'
EMBED_BATCH_SIZE = 10

tokenizer = BertTokenizer.from_pretrained(BERT_MODEL_VERSION)
model = BertModel.from_pretrained(BERT_MODEL_VERSION)
model.eval()


def get_embeddings(documents):
    all_indexed_tokens = []

    with torch.no_grad():
        for text in documents:
            tokenized_text = (
                [tokenizer.cls_token] +
                tokenizer.tokenize(text) +
                [tokenizer.sep_token]
            )

            indexed_tokens = tokenizer.convert_tokens_to_ids(
                tokenized_text,
            )

            all_indexed_tokens.append(torch.tensor(indexed_tokens))

        tokens_tensor = pad_sequence(
            all_indexed_tokens,
            batch_first=True,
        )

        attention_mask = torch.where(
            tokens_tensor != 0,
            torch.ones(tokens_tensor.shape),
            torch.zeros(tokens_tensor.shape),
        )

        hidden_states, _ = model(
            tokens_tensor,
            attention_mask=attention_mask,
        )

        # 0th element of 1st dim is CLS token
        return hidden_states[:, 0, :]
