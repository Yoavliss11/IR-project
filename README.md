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
 -  Additionally, a pickle-based dictionary is used to map Wikipedia document IDs to their corresponding article titles. This mapping is applied only at the presentation stage and is not involved in the retrieval or ranking process.


## Search Capabilities - Main Search Function
The system exposes a single primary search function. Document retrieval and ranking are performed exclusively using the body index, with cosine similarity over TF-IDF vectors serving as the sole scoring mechanism. PageRank was empirically evaluated as an additional ranking signal, but did not lead to measurable improvements in retrieval quality and was therefore excluded from the final ranking pipeline.


## Infrastructure and Deployment
 - All indexes and auxiliary data are stored on Google Cloud Storage.
 - The search engine is deployed on a Google Cloud virtual machine and exposed via a REST API.
 - Queries can be sent through the /search?query=YOUR_QUERY endpoint once the server is running.

## Project Contributors

Einav Rahamim – einavra@post.bgu.ac.il | Yoav Liss – yoavlis@post.bgu.ac.il

If there is a problem to access to the virtual machine or additional project details, please contact the authors.

The external IP address of a VM: http://136.113.68.179:8080/
