import pandas as pd
import chainlit as cl
import time
from langchain_huggingface import (
    HuggingFaceEndpointEmbeddings,
    HuggingFaceEndpoint,
    HuggingFaceEmbeddings,
)
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from emoji import replace_emoji
import os

load_dotenv()
# Hugging Face API token (replace with your actual token)
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
if not HUGGINGFACE_API_TOKEN:
    raise ValueError("HUGGINGFACE_API_TOKEN not found in environment variables")


# Remove emojis from texts
def preprocess_text(text):
    text = replace_emoji(text, replace="")
    return text.lower()


# Load the CSV file
def load_data(use_sample=True):
    try:
        df = pd.read_csv("./data/raw/SPOTIFY_REVIEWS.csv")
        if use_sample:
            df = df.sample(300)
        return df[["review_text", "review_rating", "review_likes"]]
    except FileNotFoundError:
        print(
            "CSV file not found. Please ensure 'SPOTIFY_REVIEWS.csv' is in the same directory as this script."
        )
        return None


# Create vector store using FAISS and default use local embeddings model
def create_vector_store(df, use_local_embeddings=True):
    try:
        if use_local_embeddings:
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-l6-v2"
            )
        else:
            embeddings = HuggingFaceEndpointEmbeddings(
                model="sentence-transformers/all-MiniLM-l6-v2",
                huggingfacehub_api_token=HUGGINGFACE_API_TOKEN,
            )
        df["cleaned_review_text"] = df["review_text"].astype(str).apply(preprocess_text)
        texts = df["cleaned_review_text"].tolist()
        vector_store = FAISS.from_texts(texts, embeddings)
        return vector_store
    except Exception as e:
        error_embeddings = f"Error creating vector store: {str(e)}"
        print(error_embeddings)
        # Add sleep to rate limit API request in case of failure
        time.sleep(60)
        return None


# Initialise Hugging Face Inference API
def init_llm():
    try:
        llm = HuggingFaceEndpoint(
            # repo_id="mistralai/Mistral-7B-Instruct-v0.3",
            repo_id="meta-llama/Meta-Llama-3-8B-Instruct",
            temperature=0.5,
            max_new_tokens=512,
            huggingfacehub_api_token=HUGGINGFACE_API_TOKEN,
        )
        return llm
    except Exception as e:
        error_llm = f"Error initializing language model: {str(e)}"
        print(error_llm)
        # Add sleep to rate limit API request in case of failure
        time.sleep(60)
        return None


# Format context docs in QA chain
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


# Create QA chain using Langchain CEL
def create_qa_chain(vector_store, llm):
    retriever = vector_store.as_retriever()
    prompt_template = """Analyze the following reviews and answer the question. If you can't find an answer, say you don't know.
    The reviews are specificallly for the Spotify app in Google App Store, any other mention of any other product unrelated to Spotify, music streaming platform and features should be dismissed. 
    Your target audiences are the management-level officers, please answer professionally and with fair amount of business knowledge.
    Context: {context}
    Question: {question}
    Answer: Let me analyze the reviews and provide an insightful answer:
    """
    qa_prompt = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )
    qa_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | qa_prompt
        | llm
        | StrOutputParser()
    )
    return qa_chain


# Quality scoring function, basically basic check whether the result is decent enough
def quality_score(answer):
    score = 0
    if len(answer.split()) > 30:  # Checks if the answer is not just snippets
        score += 1
    if any(
        keyword in answer.lower()
        for keyword in ["analysis", "insight", "trend", "recommendation"]
    ):
        score += 1
    if answer.count(".") > 2:  # Checks if the answer has multiple sentences
        score += 1
    return min(score, 3)  # Max score is 3


@cl.on_chat_start
async def init():
    df = load_data(use_sample=False)
    if df is not None:
        # Use
        vector_store = create_vector_store(df)
        if vector_store is not None:
            llm = init_llm()
            if llm is not None:
                qa_chain = create_qa_chain(vector_store, llm)
                cl.user_session.set("qa_chain", qa_chain)
                await cl.Message("Reviews Q&A Tool is ready. Ask your question!").send()
            else:
                await cl.Message(
                    "Failed to initialize the language model. Please check your Hugging Face API token and internet connection."
                ).send()
        else:
            await cl.Message(
                "Failed to create the vector store. Please check your data and embeddings setup."
            ).send()
    else:
        await cl.Message("Failed to load the data. Please check your CSV file.").send()


@cl.on_message
async def main(message: cl.Message):
    qa_chain = cl.user_session.get("qa_chain")
    if qa_chain is not None:
        try:
            response = qa_chain.invoke(message.content)
            print(response)
            score = quality_score(response)
            answer = f"""{response}\n ------\n Answer Quality Score: {score}/3"""
            await cl.Message(answer).send()
        except Exception as e:
            error_main = f"Error generating response: {str(e)}"
            await cl.Message(error_main).send()
    else:
        await cl.Message(
            "QA system is not initialized. Please restart the chat."
        ).send()
