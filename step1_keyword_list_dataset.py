# -*- coding: utf-8 -*-
"""Step1_Keyword_List_Dataset.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1WiPX7Ba414wjETzzteQeSNaWiWUtOx_-

# Import packages
"""

from google.colab import drive
drive.mount('/content/drive')

!pip install datasets

import pandas as pd
import datasets
from tqdm import tqdm

"""# Dataset

"""

from datasets import load_dataset

dataset = load_dataset("cnn_dailymail", '3.0.0')

dataset

# dataset type 'datsaet'
print(type(dataset))

# convert to pandas dataframe
df_cnn_train = pd.DataFrame(dataset['train'])
df_cnn_valid = pd.DataFrame(dataset['validation'])
df_cnn_test = pd.DataFrame(dataset['test'])

# concatenate to make full dataframe
## 데이터셋 전체에 작업해서 보내드리면 되는 것 같아서, 일단 전부 concat해뒀습니다.
df_cnn = pd.concat([df_cnn_train, df_cnn_valid, df_cnn_test], axis=0)
df_cnn = df_cnn.reset_index(drop=True)
df_cnn.head()

df_cnn.shape

"""# Model

### Candidate Selection
"""

corpus = list(df_cnn['article'])[:3]
# corpus

from sklearn.feature_extraction.text import CountVectorizer
import spacy

# CountVecotrizer _ Extract n-gram candidate 
n_gram_range = (1, 2)
stop_words = 'english' # use built-in stop word list for English


candidates_list = []

for doc in corpus :

    # Extract candidate words/phrases
    vectorizer = CountVectorizer(ngram_range=n_gram_range, stop_words=stop_words)
    count = vectorizer.fit_transform([doc])
    all_candidates = vectorizer.get_feature_names_out()
    ## ngram_candidates.append(all_candidates)

    # Extract only noun words (POS tagging)
    nlp = spacy.load('en_core_web_sm')
    nlp_doc = nlp(doc)
    noun_phrases = set(chunk.text.strip().lower() for chunk in nlp_doc.noun_chunks)
    nouns = set()
    for token in nlp_doc : 
        if token.pos_ =="NOUN":
            nouns.add(token.text)
    all_nouns = nouns.union(noun_phrases) # union noun words/phrases       

    # Filter all noun candidate 
    noun_candidates  =list(filter(lambda candidate: candidate in all_nouns, all_candidates))

    candidates_list.append(noun_candidates)

# first 10 keywords from the first document
candidates_list[0][:10]

"""### KeyWord Extraction"""

!pip install transformers

# load tokenizer and model
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

tokenizer = AutoTokenizer.from_pretrained("bloomberg/KeyBART")

model = AutoModelForSeq2SeqLM.from_pretrained("bloomberg/KeyBART")

from sklearn.metrics.pairwise import cosine_similarity

all_keywords = []

for i in range(3):
    
    candidate_tokens = tokenizer(candidates_list[i], padding=True, return_tensors="pt")['input_ids']
    candidate_embeddings = model(candidate_tokens)['encoder_last_hidden_state']
    article_tokens = tokenizer([df_cnn['article'][i]], padding=True, return_tensors="pt")['input_ids']
    article_embedding = model(article_tokens)['encoder_last_hidden_state']

    candidate_embeddings = candidate_embeddings.detach().numpy()
    article_embedding = article_embedding.detach().numpy()

    top_k = 10
    distances = cosine_similarity(candidate_embeddings, article_embedding)
    keywords = [candidates_list[i][index] for index in distances.argsort()[0][-top_k:]]

    all_keywords.append(keywords)



candidate_tokens = tokenizer(candidates_list[i], padding=True, return_tensors="pt")['input_ids']

print(candidate_tokens.shape)

article_tokens = tokenizer([df_cnn['article'][0]], padding=True, return_tensors="pt")['input_ids']

print(article_tokens.shape)

candidate_embeddings = model(candidate_tokens)['encoder_hidden_states']

article_embedding = model(article_tokens)['encoder_hidden_states']

"""### reference (bert) (temp)"""

from transformers import AutoModel, AutoTokenizer

model_name = "distilroberta-base"
model_2 = AutoModel.from_pretrained(model_name)
tokenizer_2 = AutoTokenizer.from_pretrained(model_name)

candidate_tokens_2 = tokenizer_2(candidates_list[0], padding=True, return_tensors="pt")
candidate_embeddings_2 = model_2(**candidate_tokens_2)["pooler_output"]

candidate_tokens_2.input_ids.shape

candidate_embeddings_2.shape

"""# Ouput"""

# save as json format





