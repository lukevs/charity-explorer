import csv
import dataclasses
import json
import os

import numpy as np
import pandas as pd
import torch
from tqdm import tqdm

from bert import get_embeddings
from utils import batch


@dataclasses.dataclass
class Charity:
    name: str
    description: str
    url: str


class CharityIndex:
    _CHARITY_FILENAME = 'charities.json'
    _EMBED_FILENAME = 'embeddings.npy'
    _INDEX_FILENAME = 'index.json'

    _EMBED_BATCH_SIZE = 10
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
                embeddings = cls._get_sentence_embeddings(
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
    def _get_sentence_embeddings(cls, description):
        embeddings_list = []

        # TODO - be smarter about this
        sentences = [
            sentence.strip() for sentence in description.split('.')
            if sentence.strip() != ''
        ]

        for sentence_batch in batch(sentences, cls._EMBED_BATCH_SIZE):
            embeddings = get_embeddings(sentence_batch)
            embeddings_list.append(embeddings)

        return torch.cat(embeddings_list)

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
        [query_embedding] = get_embeddings([query])
        query_embedding_normalized = (
            query_embedding /
            torch.norm(query_embedding, p=2)
        )

        similarities = torch.matmul(
            self._embeddings_normalized,
            query_embedding_normalized.t(),
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