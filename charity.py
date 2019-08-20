import csv
import dataclasses
import json
import os

import numpy as np
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
    _EMBED_BATCH_SIZE = 10

    def __init__(self, charities, embeddings):
        self._charities = charities
        self._embeddings = embeddings

    @classmethod
    def build(cls, charities):
        embeddings_list = []

        with tqdm(total=len(charities)) as progress_bar:
            for charity_batch in batch(charities, cls._EMBED_BATCH_SIZE):
                descriptions = [
                    charity.description
                    for charity in charity_batch
                ]

                embeddings_list.append(get_embeddings(descriptions))
                progress_bar.update(len(charity_batch))

        embeddings = torch.cat(embeddings_list)

        return cls(charities, embeddings)

    @classmethod
    def build_from_csv(cls, csv_path):
        """expects columns name, description, and url"""

        with open(csv_path, 'r') as csv_file:
            reader = csv.DictReader(csv_file)
            charities = [
                Charity(**row)
                for row in reader
            ]

            return cls.build(charities)

    @classmethod
    def load(cls, path):
        charity_path = cls._get_charity_path(path)
        embeddings_path = cls._get_embeddings_path(path)

        with open(charity_path, 'r') as charity_file:
            charity_data = json.load(charity_file)
            charities = [
                Charity(**charity_entry)
                for charity_entry in charity_data
            ]

        embeddings = torch.tensor(np.load(embeddings_path))

        return cls(charities, embeddings)

    def save(self, path):
        charity_path = self._get_charity_path(path)
        embeddings_path = self._get_embeddings_path(path)

        with open(charity_path, 'w') as charity_file:
            charity_data = [
                dataclasses.asdict(charity)
                for charity in self._charities
            ]

            json.dump(charity_data, charity_file)

        np.save(embeddings_path, self._embeddings.numpy())

    def search(self, query, top_n=5):
        [query_embedding] = get_embeddings([query])

        distances = torch.norm(
            self._embeddings - query_embedding,
            p=2,
            dim=1,
        )

        best_match_indices = torch.argsort(distances)[:top_n]

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
