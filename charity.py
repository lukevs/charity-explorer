import csv
import dataclasses
import json
import os
import re

import numpy as np
import pandas as pd
import torch
from nltk.tokenize import sent_tokenize
from tqdm import tqdm
from torch.nn.functional import cosine_similarity

from bert import embed
from utils import batch


MAX_SENTENCE_LENGTH = 512


def _get_embedding_similarities(query_embedding, document_embeddings):
    return cosine_similarity(
        query_embedding,
        document_embeddings,
        dim=1,
    )


def _get_sentence_embeddings(description, embed_batch_size=10):
    embeddings_list = []

    sentences = [
        re.sub('\[\d+\]', '', sent).strip().lower()[:MAX_SENTENCE_LENGTH]
        for sent in sent_tokenize(description)
    ]

    for sentence_batch in batch(sentences, embed_batch_size):
        embeddings = embed(sentence_batch)
        embeddings_list.append(embeddings)

    return torch.cat(embeddings_list)



@dataclasses.dataclass
class Charity:
    name: str
    description: str
    url: str


class CharityIndex:
    _CHARITY_FILENAME = 'charities.json'
    _EMBED_FILENAME = 'embeddings.npy'
    _INDEX_FILENAME = 'index.json'

    _SEARCH_TOP_N_SENTENCES = 1

    def __init__(self, charities, embeddings, embeddings_charity_index):
        self._charities = charities
        self._embeddings = embeddings
        self._embeddings_charity_index = embeddings_charity_index

        self._embeddings_normalized = (
            self._embeddings /
            torch.norm(self._embeddings, p=2, dim=0)
        )

    @classmethod
    def build(cls, charities):
        embeddings_charity_index = []
        embeddings_list = []

        with tqdm(total=len(charities)) as progress_bar:
            for charity_index, charity in enumerate(charities):
                embeddings = _get_sentence_embeddings(
                    charity.description,
                )

                embeddings_charity_index += (
                    [charity_index] * len(embeddings)
                )

                embeddings_list.append(embeddings)
                progress_bar.update(1)

        embeddings = torch.cat(embeddings_list)

        return cls(
            charities,
            embeddings,
            embeddings_charity_index,
        )

    @classmethod
    def build_from_tsv(cls, tsv_path):
        """expects columns name, description, and url"""

        with open(tsv_path, 'r') as tsv_file:
            reader = csv.DictReader(tsv_file, dialect='excel-tab')
            charities = [
                Charity(**row)
                for row in reader
            ]

            return cls.build(charities)

    @classmethod
    def load(cls, path):
        charity_path = cls._get_charity_path(path)
        embeddings_path = cls._get_embeddings_path(path)
        index_path = cls._get_index_path(path)

        with open(charity_path, 'r') as charity_file:
            charity_data = json.load(charity_file)
            charities = [
                Charity(**charity_entry)
                for charity_entry in charity_data
            ]

        with open(index_path, 'r') as index_file:
            embeddings_charity_index = json.load(index_file)

        embeddings = torch.tensor(np.load(embeddings_path))

        return cls(
            charities,
            embeddings,
            embeddings_charity_index,
        )

    def save(self, path):
        charity_path = self._get_charity_path(path)
        embeddings_path = self._get_embeddings_path(path)
        index_path = self._get_index_path(path)

        with open(charity_path, 'w') as charity_file:
            charity_data = [
                dataclasses.asdict(charity)
                for charity in self._charities
            ]

            json.dump(charity_data, charity_file)

        with open(index_path, 'w') as index_file:
            json.dump(
                self._embeddings_charity_index,
                index_file,
            )

        np.save(embeddings_path, self._embeddings.numpy())

    def search(self, query, top_n=5):
        query_embedding = embed([query])
        similarities = _get_embedding_similarities(
            query_embedding,
            self._embeddings,
        )

        charity_similarities = pd.DataFrame({
            'charity': self._embeddings_charity_index,
            'similarity': similarities,
        })

        best_match_indices = (charity_similarities
            .sort_values('similarity', ascending=False)
            .groupby('charity')
            .head(self._SEARCH_TOP_N_SENTENCES)
            .groupby('charity')
            .mean()
            .sort_values('similarity', ascending=False)
            .head(top_n)
            .index
            .tolist())

        return [
            self._charities[i]
            for i in best_match_indices
        ]

    @classmethod
    def _get_charity_path(cls, path):
        return os.path.join(path, cls._CHARITY_FILENAME)

    @classmethod
    def _get_embeddings_path(cls, path):
        return os.path.join(path, cls._EMBED_FILENAME)

    @classmethod
    def _get_index_path(cls, path):
        return os.path.join(path, cls._INDEX_FILENAME)
