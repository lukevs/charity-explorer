#!/bin/sh

# download fastText vectors used in the model
mkdir fastText
curl -Lo fastText/crawl-300d-2M.vec.zip https://dl.fbaipublicfiles.com/fasttext/vectors-english/crawl-300d-2M.vec.zip
unzip fastText/crawl-300d-2M.vec.zip -d fastText/
rm fastText/crawl-300d-2M.vec.zip

# download the model itself
mkdir encoder
curl -Lo encoder/infersent2.pkl https://dl.fbaipublicfiles.com/infersent/infersent2.pkl

# download InferSent model
git clone https://github.com/facebookresearch/InferSent --depth=1
touch InferSent/__init__.py
