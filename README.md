# review-chatbot

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

Build a chatbot for management to answer questions regarding the reviews in Google App Store

Currently using sample data from all of the reviews collected for development purpose and due to resource limitation. 

Embedding model can be run locally or through free Hugging Face Inference API, by default runs locally as embedding model are small enough and not resource heavy.

For the LLM, the app fully relies on free Hugging Face Inference API, as my machine simply cannot support an LLM model nor do I have the credits for paid API.

For Embedding, the model of choice is: **sentence-transformers/all-MiniLM-l6-v2**

For the LLM, the model currently used is: **meta-llama/Meta-Llama-3-8B-Instruct**

For the UI I have taken the liberty to implement Chainlit instead of Streamlit as it is a much sleeker look for the purpose of chatbot rather than Streamlit.

As the data is rather large, I have decided not to push it into LFS and may be [downloaded before usage.

## Preview 
[Video](./references/app-recording.mov)

## How To

In both methods, you need to have a Hugging Face Token in your `.env`, as shown in `.env.sample`

### Launch Locally 

1. Download the review data into `/data/raw/`
2. Install dependencies using Python 3.11 `pip install -r requirements.txt`
3. Launch Chainlit app with `chainlit run app.py -w`

### Launch with Docker
1. Download the review data into `/data/raw/`
2. Create docker image `docker build -t review-chatbot-app .`
3. Launch docker image `docker run -d --publish=8000:8000 --name=review-chatbot review-chatbot-app`

## Project Organization

```
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.cfg          <- Configuration file for flake8
│
└── src                <- Source code for use in this project.
    │
    ├── __init__.py             <- Makes review_chatbot a Python module
    │
    ├── config.py               <- Store useful variables and configuration
    │
    ├── dataset.py              <- Scripts to download or generate data

```

--------

