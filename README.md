# IR-project
Building a search engine for English Wikipedia


This project was developed as the final assignment for the Information Retrieval course at Ben-Gurion University. The goal was to design and implement a scalable search engine over the English Wikipedia corpus, supporting efficient retrieval from more than six million articles. The system was built with a strong emphasis on ranking quality, response time, and robustness under large-scale data.


## Core Retrieval Techniques 
The search engine combines multiple classic and advanced information retrieval methods in order to maximize relevance: 
 - Inverted Index for fast term-based lookup
 - TF-IDF for term weighting Cosine Similarity for vector-based matching
 - PageRank to incorporate link structure importance

## Indexes Used
The retrieval system is based on a single index:
 - Body Index – built from the full text of Wikipedia articles and used as the sole source for document retrieval and ranking.
 - Title Index – built from Wikipedia article titles and used as an additional textual signal to improve matching quality for queries that are strongly aligned with document titles.
 - PageRank – a global importance score computed over the Wikipedia link graph and incorporated as an auxiliary ranking signal to refine the final ordering of retrieved documents.
 -  Additionally, a pickle-based dictionary is used to map Wikipedia document IDs to their corresponding article titles. This mapping is applied only at the presentation stage and is not involved in the retrieval or ranking process.


## Search Capabilities - Main Search Function
The system exposes a single primary search function. Document retrieval and ranking are performed using a combination of textual and global signals. Textual relevance is computed using cosine similarity over TF-IDF vectors derived from both the body index and the title index, with a weighted combination that assigns a higher importance to the body content. Specifically, 60% of the textual score is attributed to the body index and 40% to the title index.

In addition, PageRank is incorporated as a global importance signal. A portion of the overall ranking score, amounting to 15%, is allocated to PageRank. This weight is taken from the combined textual score, resulting in an effective contribution of PageRank that is smaller than the original textual weights, while preserving the dominance of content-based relevance in the final ranking pipeline.


## Infrastructure and Deployment
 - All indexes and auxiliary data are stored on Google Cloud Storage.
 - The search engine is deployed on a Google Cloud virtual machine and exposed via a REST API.
 - Queries can be sent through the /search?query=YOUR_QUERY endpoint once the server is running.

## Project Contributors

Einav Rahamim – einavra@post.bgu.ac.il | Yoav Liss – yoavlis@post.bgu.ac.il

If there is a problem to access to the virtual machine or additional project details, please contact the authors.

The external IP address of a VM: http://35.232.187.200:8080/
