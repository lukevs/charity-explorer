import torch
from pytorch_transformers import BertForNextSentencePrediction
from pytorch_transformers import BertTokenizer
from torch.nn.functional import cosine_similarity
from torch.nn.functional import softmax
from torch.nn.utils.rnn import pad_sequence


BERT_MODEL_VERSION = 'bert-base-uncased'
MAX_SENTENCE_LENGTH = 512


tokenizer = BertTokenizer.from_pretrained(BERT_MODEL_VERSION)
model = BertForNextSentencePrediction.from_pretrained(
    BERT_MODEL_VERSION,
    output_hidden_states=True,
)

model.eval()

if torch.cuda.is_available():
    model.cuda()


def calculate_similarities(
        query_embedding,
        document_embeddings,
    ):

    return cosine_similarity(
        query_embedding,
        document_embeddings,
        dim=1,
    )


def calculate_next_sentence_probability(query, sentences):
    all_indexed_tokens = []
    tokenized_query = tokenizer.tokenize(query)
    max_sentence_length = (
        MAX_SENTENCE_LENGTH -
        2 -
        len(tokenized_query)
    )

    for sentence in sentences:
        tokenized_text = (
            [tokenizer.cls_token] +
            tokenizer.tokenize(query) +
            [tokenizer.sep_token] +
            tokenizer.tokenize(sentence)[:max_sentence_length] +
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

    if torch.cuda.is_available():
        tokens_tensor = tokens_tensor.cuda()
        attention_mask = attention_mask.cuda()

    with torch.no_grad():
          outputs = model(
              tokens_tensor,
              attention_mask=attention_mask,
          )

    return softmax(outputs[0])[:, 0]


def embed_sentences(sentences):
  all_indexed_tokens = []
 
  for text in sentences:
      tokenized_text = (
          [tokenizer.cls_token] +
          tokenizer.tokenize(text[:MAX_SENTENCE_LENGTH - 2]) +
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
  
  if torch.cuda.is_available():
    tokens_tensor = tokens_tensor.cuda()
    attention_mask = attention_mask.cuda()

  with torch.no_grad():
        output = model.bert(
            tokens_tensor,
            attention_mask=attention_mask,
        )

  return output[2][-11].mean(axis=1)
