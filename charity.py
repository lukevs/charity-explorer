import csv
import dataclasses
import json
import os
import re

import nltk
import numpy as np
import pandas as pd
import torch
from InferSent.models import InferSent
from nltk.tokenize import sent_tokenize
from tqdm import tqdm

from utils import batch

nltk.download('punkt')

MODEL_VERSION = 2
MODEL_PATH = 'encoder/infersent%s.pkl' % MODEL_VERSION
MODEL_PARAMS = {
    'bsize': 64,
    'word_emb_dim': 300,
    'enc_lstm_dim': 2048,
    'pool_type': 'max',
    'dpout_model': 0.0,
    'version': MODEL_VERSION
}
W2V_PATH = 'fastText/crawl-300d-2M.vec'


@dataclasses.dataclass
class Charity:
    name: str
    description: str
    url: str


class CharityIndex:
    _CHARITY_FILENAME = 'charities.json'
    _EMBED_FILENAME = 'embeddings.npy'
    _INDEX_FILENAME = 'index.json'

    _SEARCH_TOP_N_SENTENCES = 4

    def __init__(self, model, charities, embeddings, embeddings_charity_index):
        self._model = model
        self._charities = charities
        self._embeddings = embeddings
        self._embeddings_charity_index = embeddings_charity_index

    @classmethod
    def _build_initialized_model(cls, initial_sentences):
        model = InferSent(MODEL_PARAMS)
        model.load_state_dict(torch.load(MODEL_PATH))
        model.set_w2v_path(W2V_PATH)
        model.build_vocab(initial_sentences, tokenize=True)

        return model

    @classmethod
    def build(cls, charities):
        embeddings_charity_index = []
        embeddings_list = []

        all_descriptions = [charity.description for charity in charities]
        model = cls._build_initialized_model(all_descriptions)

        with tqdm(total=len(charities)) as progress_bar:
            for charity_index, charity in enumerate(charities):
                embeddings = cls._get_sentence_embeddings(
                    model,
                    charity.description,
                )

                embeddings_charity_index += (
                    [charity_index] * len(embeddings)
                )

                embeddings_list.append(embeddings)
                progress_bar.update(1)

        embeddings = torch.cat(embeddings_list)

        return cls(
            model,
            charities,
            embeddings,
            embeddings_charity_index,
        )

    @classmethod
    def _get_sentence_embeddings(cls, model, description):
        sentences = [
            cls._clean_sentence(sentence)
            for sentence in sent_tokenize(description)
        ]

        return torch.tensor(model.encode(
            sentences,
            tokenize=True,
        ))

    @staticmethod
    def _clean_sentence(text):
        return re.sub(r'\[\w+\]\s+?', '', text).strip()

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

        all_descriptions = [charity.description for charity in charities]
        model = cls._build_initialized_model(all_descriptions)

        return cls(
            model,
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
        [query_embedding] = torch.tensor(self._model.encode([query]))
        similarities = -torch.norm(
            self._embeddings - query_embedding,
            p=2,
            dim=1,
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
