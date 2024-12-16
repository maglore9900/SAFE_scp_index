from modules import adapter
import environ

# env = environ.Env()
# environ.Env.read_env()

# ad = adapter.Adapter(env)

# results = ad.query_datastore("scp")
# print(results)

from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import FAISS


model_name = "BAAI/bge-small-en"
# model_name = "BAAI/bge-base-en-v1.5"
model_kwargs = {"device": "cpu"}
encode_kwargs = {"normalize_embeddings": True}
embeddings = HuggingFaceBgeEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs,
)
# import faiss

# index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))

from datetime import datetime
# print(results)
# from langchain_community.vectorstores import FAISS
# vectorstore = FAISS(
#     embedding_function=embeddings,
#     index=index,
#     docstore="scp_data",
#     index_to_docstore_id={},
# )

load_start = datetime.now()
vectorstore = FAISS.load_local("scp_data", embeddings, allow_dangerous_deserialization=True)
load_finish = datetime.now()

search_start = datetime.now()

results = vectorstore.similarity_search(
    "scp-010",
    k=2,
    filter={"SCP_ID": "SCP-010"},
)
search_finish = datetime.now()
# for res in results:
print(results)
print(f"load time: {load_finish - load_start}\n search time: {search_finish - search_start}")
#     print(f"* {res.page_content} [{res.metadata}]")