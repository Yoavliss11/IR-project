import sys
import os
import re
import math
import pickle
from collections import defaultdict
from contextlib import closing

sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # Ensure current directory is in PYTHONPATH

from inverted_index_gcp import MultiFileReader, InvertedIndex


# *********
# Constants
# *********
N_DOCS = 6_348_910
INDEX_NAME = "index"
TUPLE_SIZE = 6

BUCKET_NAME = "bucket_324041060"
POSTINGS_DIR = "postings_gcp"
TITLES_PKL_PATH = "/home/einavra/title_id.pkl"
TITLE_INDEX_NAME = "title_index"
TITLE_POSTINGS_DIR = "title_index/postings_gcp_title_index"


# ************************************
# Load inverted index - local pkl only
# ************************************
def load_local_index(index_name):
    idx = InvertedIndex.read_index(".", index_name)
    for term, locs in idx.posting_locs.items():
        idx.posting_locs[term] = [(os.path.basename(fname), offset) for fname, offset in locs]
    return idx

inverted = load_local_index(INDEX_NAME)
inverted_title = load_local_index(TITLE_INDEX_NAME)


# *********
# Tokenizer
# *********
RE_WORD = re.compile(r"""[\#\@\w](['\-]?\w){2,24}""", re.UNICODE)

def tokenize_query(query):
    return [m.group().lower() for m in RE_WORD.finditer(query)]


# *************************
# Posting list reader (GCS)
# *************************
def read_posting_list(inverted, w, postings_dir):
    with closing(MultiFileReader(postings_dir, bucket_name=BUCKET_NAME)) as reader:
        locs = inverted.posting_locs[w]
        b = reader.read(locs, inverted.df[w] * TUPLE_SIZE)

        posting_list = []
        for i in range(inverted.df[w]):
            doc_id = int.from_bytes(b[i*TUPLE_SIZE : i*TUPLE_SIZE+4], 'big')
            tf = int.from_bytes(b[i*TUPLE_SIZE+4 : (i+1)*TUPLE_SIZE], 'big')
            posting_list.append((doc_id, tf))

        return posting_list


# ****************************
# Search logic (TF-IDF cosine)
# ****************************
def simple_search(inverted, query, postings_dir):
    tokens = tokenize_query(query)
    if not tokens:
        return {}

    tf_query = defaultdict(int)
    for t in tokens:
        tf_query[t] += 1

    scores = defaultdict(float)
    query_norm = 0.0

    for term, tf_q in tf_query.items():
        if term not in inverted.df:
            continue

        df = inverted.df[term]
        idf = math.log((N_DOCS + 1) / (df + 1))

        w_tq = tf_q * idf
        query_norm += w_tq ** 2

        posting_list = read_posting_list(inverted, term, postings_dir)
        for doc_id, tf_td in posting_list:
            w_td = tf_td * idf
            scores[doc_id] += w_td * w_tq

    query_norm = math.sqrt(query_norm)
    if query_norm == 0:
        return {}

    for doc_id in scores:
        scores[doc_id] /= query_norm

    return scores


def search_engine(inverted, query, postings_dir, k=100):
    scores = simple_search(inverted, query, postings_dir)
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked[:k]


# ***********************************
# Titles dictionary (local clean PKL)
# ***********************************
_titles_dict = None

def load_titles_dict():
    global _titles_dict
    if _titles_dict is not None:
        return _titles_dict

    with open(TITLES_PKL_PATH, "rb") as f:
        _titles_dict = pickle.load(f)

    return _titles_dict


def fetch_titles_for_ids(wiki_ids):
    titles = load_titles_dict()
    return {int(doc_id): titles.get(int(doc_id)) for doc_id in wiki_ids}


# **********
# Public API
# **********
def search_api(query, k=100, body_weight=0.6, title_weight=0.4):
    # normalize weights to sum to 1
    w_sum = body_weight + title_weight
    if w_sum <= 0:
        body_w, title_w = 0.6, 0.4
    else:
        body_w = body_weight / w_sum
        title_w = title_weight / w_sum
    body_ranked = search_engine(inverted, query, POSTINGS_DIR, k=k*5)
    title_ranked = search_engine(inverted_title, query, TITLE_POSTINGS_DIR, k=k*5)

    body_scores = {doc_id: score for doc_id, score in body_ranked}
    title_scores = {doc_id: score for doc_id, score in title_ranked}

    body_max = max(body_scores.values()) if body_scores else 0.0
    title_max = max(title_scores.values()) if title_scores else 0.0

    combined = defaultdict(float)

    if body_max > 0:
        for doc_id, s in body_scores.items():
            combined[doc_id] += body_w * (s / body_max)

    if title_max > 0:
        for doc_id, s in title_scores.items():
            combined[doc_id] += title_w * (s / title_max)

    ranked = sorted(combined.items(), key=lambda x: x[1], reverse=True)[:k]
    top_ids = [doc_id for doc_id, _ in ranked]

    id_to_title = fetch_titles_for_ids(top_ids)

    results = []
    for doc_id, _ in ranked:
        title = id_to_title.get(int(doc_id))
        if title is not None:
            results.append((int(doc_id), title))

    return results
