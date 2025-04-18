# -*- coding: utf-8 -*-
"""Success with gemini.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1RfyW8il6AfyVRkMmKSRDiP9GdAgzfbeD
"""

pip install langchain_huggingface langchain_community pypdf langchain_google_genai

from langchain_huggingface import HuggingFaceEmbeddings
from pypdf import PdfReader
from langchain.text_splitter import CharacterTextSplitter
# import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

pip install faiss-cpu

import faiss

# Commented out IPython magic to ensure Python compatibility.
# %env GOOGLE_API_KEY="AIzaSyDtBgIdqYJvAiP-4XbL4hlQ2k1CrlKDlOg"

pdf_docs = ["/content/test.pdf"]

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

text = ""

for pdf in pdf_docs:
  pdf_reader = PdfReader(pdf)
  for page in pdf_reader.pages:
    text += page.extract_text()

print(text)

text_splitter = CharacterTextSplitter(
        separator='\n',
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )

chunks = text_splitter.split_text(text)

print(chunks)

embedding_dim = len(embeddings.embed_query(text))
index = faiss.IndexFlatL2(embedding_dim)

vector_store = FAISS(
    embedding_function=embeddings,
    index=index,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={},
)

print(vector_store)

def get_conversation_chain(vector_store):
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-001")

    memory = ConversationBufferMemory(memory_key='chat_history',
                                        return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(),
        memory=memory
    )
    return conversation_chain

user_question = input("Ask a question about your documents:")

def handle_user_input(user_question):
  conversation = get_conversation_chain(vector_store)
  response = ({'question': user_question})
  response = conversation(response)
  print(response)

handle_user_input(user_question)

