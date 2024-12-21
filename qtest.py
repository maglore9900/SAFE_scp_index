from transformers import AutoTokenizer
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import FAISS
from datetime import datetime

model_name = "BAAI/bge-small-en"
model_kwargs = {"device": "cpu"}
encode_kwargs = {"normalize_embeddings": True}
embeddings = HuggingFaceBgeEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs,
)


# Only used to get at token count, not necessary for the actual query
tokenizer = AutoTokenizer.from_pretrained(model_name)


load_start = datetime.now()
vectorstore = FAISS.load_local("backup", embeddings, allow_dangerous_deserialization=True)
load_finish = datetime.now()

search_start = datetime.now()

results = vectorstore.similarity_search(
    "scp-010",
    k=2,
    filter={"SCP_ID": "SCP-010"},
)
search_finish = datetime.now()

print(f"load time: {load_finish - load_start}\n search time: {search_finish - search_start}")
for result in results:
    print(len(result.page_content))
    print(len(tokenizer.encode(result.page_content)))
