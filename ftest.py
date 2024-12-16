

from langchain_openai import OpenAIEmbeddings
from uuid import uuid4
from time import sleep
import tiktoken
from pathlib import Path
import re

# embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.documents import Document
import environ

env = environ.Env()
environ.Env.read_env()

# 1



# # Get the encoding for a specific model
# encoding = tiktoken.get_encoding("cl100k_base")

# # Encode text into tokens
# text = "This is an example sentence."
# tokens = encoding.encode(text)

# # Decode tokens back to text
# decoded_text = encoding.decode(tokens)

# # Count the number of tokens in a text string
# token_count = len(encoding.encode(text))

from langchain_community.embeddings import HuggingFaceBgeEmbeddings

model_name = "BAAI/bge-small-en"
# model_name = "BAAI/bge-base-en-v1.5"
model_kwargs = {"device": "cpu"}
encode_kwargs = {"normalize_embeddings": True}
embeddings = HuggingFaceBgeEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs,
)

index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))

vectorstore = FAISS(
    embedding_function=embeddings,
    index=index,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={},
)



documents = []
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
entry = []
UUID = 0
pattern = r"^Identifier: (SCP-\d+)$"
with open('test.txt', 'r') as file:
    f = file.read()
    for g in f.split('",'):
        print(f"UUID {UUID}")
        print(len(g))
        scp_name = None
        lines = g.split('\n')
        for l in lines:
            l = re.sub(r'^"','', l)
            entry.append(f"{l}\n")
            match = re.match(pattern, l)
            if match:
                scp_name = match.group(1)
            # if re.match(pattern, l):
            #     scp_name = l
        content = ' '.join(entry)
        print(f"setting document object for {scp_name}")
        document = Document(
            page_content=content,
            metadata={"SCP_ID": scp_name},
        )
        documents.append(document)
        print("writing to datastore")
        if not Path("scp_data/store.faiss").exists():
            vectorstore.add_documents(documents=documents)
            vectorstore.save_local(f"scp_data/")
            documents = []
            sleep(3)
        else:
            vectorstore.add_documents(documents=documents)
            old_vectorstore = FAISS.load_local("scp_data", embeddings, allow_dangerous_deserialization=True)
            old_vectorstore.merge_from(tmp_vectorstore)
            old_vectorstore.save_local("scp_data/")
            documents = []
        print(f"Successfully added uuid {UUID} to the datastore.")
        UUID += 1
        if UUID >= 2000:
            break
        

        

