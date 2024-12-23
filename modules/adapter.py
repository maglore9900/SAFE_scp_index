
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
    UnstructuredODTLoader,
    UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredExcelLoader,
    UnstructuredCSVLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQAWithSourcesChain, RetrievalQA

from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient, models

from langchain_core.documents import Document
from pathlib import Path
from typing import Dict
from modules import prompts
import re



class Adapter:
    def __init__(self, env):
        self.llm_text = env("LLM_TYPE")
        self.char_prompt = getattr(prompts, "safe", "You are a helpful assistant.")
        self.char_prompt = self.char_prompt + "\n<USER QUERY>{query}</USER QUERY>"
        from langchain_huggingface import HuggingFaceEmbeddings
        # model_name = "BAAI/bge-small-en"
        model_name = "BAAI/bge-large-en-v1.5"
        model_kwargs = {"device": "cuda"}
        encode_kwargs = {"normalize_embeddings": True}
        embedding = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs,
        )
        client = QdrantClient(path="qdb")

        self.vectorstore = QdrantVectorStore(
            client=client,
            collection_name="scp_collection",
            embedding=embedding,
        )
        # self.vector_store = FAISS.load_local("backup", embedding, allow_dangerous_deserialization=True)
        if self.llm_text.lower() == "openai":
            from langchain_openai import OpenAIEmbeddings, ChatOpenAI
            from phi.model.openai import OpenAIChat
            self.model = OpenAIChat(id=env("OPENAI_MODEL"))
            self.model2 = OpenAIChat(id=env("OPENAI_MODEL2", default=env("OPENAI_MODEL")))
            self.prompt = ChatPromptTemplate.from_template(
                "answer the following request: {query}"
            )
            self.llm_chat = ChatOpenAI(model_name=env("OPENAI_MODEL"), temperature=0.4)
            self.model = OpenAIChat(id=env("OPENAI_MODEL"))
            self.embedding = OpenAIEmbeddings(model="text-embedding-ada-002")
        elif self.llm_text.lower() == "local":
            from langchain_huggingface import HuggingFaceEmbeddings

            # from langchain_community.chat_models import ChatOllama
            from langchain_ollama import ChatOllama, OllamaLLM
            from phi.model.ollama import Ollama
            from phi.agent import Agent
            self.model = Ollama(id=env("LOCAL_MODEL"))
            self.model2 = Ollama(id=env("LOCAL_MODEL2", default=env("LOCAL_MODEL")))
            # from langchain_community.llms import Ollama
            self.ollama_url = env("OLLAMA_URL")
            self.local_model = env("LOCAL_MODEL")
            self.llm = OllamaLLM(base_url=self.ollama_url, model=self.local_model)
            self.prompt = ChatPromptTemplate.from_template(
                "answer the following request: {query}"
            )
            self.llm_chat = ChatOllama(
                base_url=self.ollama_url, model=self.local_model
            )
            model_name = "BAAI/bge-small-en"
            model_kwargs = {"device": "cpu"}
            encode_kwargs = {"normalize_embeddings": True}
            self.embedding = HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs=model_kwargs,
                encode_kwargs=encode_kwargs,
            )
        else:
            raise ValueError("Invalid LLM")

    def add_to_datastore(self, filename):
        try:
            doc = self.load_document(f"{filename}")
            vectorstore_path = Path("vector_store")
            
            # Check if the vector_store directory exists and contains the index files
            if not (vectorstore_path.exists() and (vectorstore_path / "index.faiss").exists() and (vectorstore_path / "index.pkl").exists()):
                print("Vector store does not exist, creating a new one.")
                vectorstore = FAISS.from_documents(doc, self.embedding)
                vectorstore.save_local("vector_store")  # Save directly to the directory
            else:
                print("Vector store exists, loading and merging.")
                existing_vectorstore = FAISS.load_local("vector_store", self.embedding, allow_dangerous_deserialization=True)
                new_vectorstore = FAISS.from_documents(doc, self.embedding)
                existing_vectorstore.merge_from(new_vectorstore)
                existing_vectorstore.save_local("vector_store")  # Save the merged index back to the same directory

            print(f"Successfully added {filename} to the datastore.")
        except Exception as e:
            print(f"An error occured: {e}")
            return(f"An error occurred: {e}")
            
    def vector_doc(self, filename):
        doc = self.load_document(filename)
        retriever = FAISS.from_documents(doc, self.embedding).as_retriever()
        return retriever

    def query_datastore(self, query):
        print("Entered function")
        try:
            result = ''
            if "scp" in query.lower():
                pattern = r'\bscp-?(\d+)\b'
                matches = re.findall(pattern, query, re.IGNORECASE)
                scp_codes = []

                for match in matches:
                    match = re.sub(r'scp', '', match, flags=re.IGNORECASE)
                    match = re.sub(r'-', '', match)
                    formatted_code = f"SCP-{match}"  
                    scp_codes.append(formatted_code)
            if scp_codes:
                for each in scp_codes:
                    data = self.vectorstore.similarity_search(
                    query,
                    k=2,
                    collection_name="scp_collection",
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                    key="metadata.SCP_ID",
                                    match=models.MatchValue(
                                        value=each,
                                    ),
                                ),
                            ]
                        )
                    )
                    for res in data:
                        result += f"{res.page_content}\n"
            else:
                data = self.vectorstore.similarity_search(
                    query,
                    k=2,
                    collection_name="scp_collection",
                )
                for res in data:
                    result += f"{res.page_content}\n"
 
            return result

        except Exception as e:
            print(f"An error occurred: {e}")
            return f"An error occurred: {e}"

    def load_document(self, filename):
        loaders = {
            ".pdf": PyPDFLoader,
            ".txt": TextLoader,
            ".csv": UnstructuredCSVLoader,
            ".doc": UnstructuredWordDocumentLoader,
            ".docx": UnstructuredWordDocumentLoader,
            ".md": UnstructuredMarkdownLoader,
            ".odt": UnstructuredODTLoader,
            ".ppt": UnstructuredPowerPointLoader,
            ".pptx": UnstructuredPowerPointLoader,
            ".xlsx": UnstructuredExcelLoader,
        }
        for extension, loader_cls in loaders.items():
            if filename.endswith(extension):
                loader = loader_cls("tmp/"+filename)
                documents = loader.load()
                break
        else:
            # raise ValueError("Invalid file type")
            print("Invalid File Type")
            return "Invalid File Type"
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=30
        )
        return text_splitter.split_documents(documents=documents)
        
    def add_content_to_datastore(self, content, meta: Dict = None, datastore="vectorstore"):
        "Adds raw content to datastore with optional metadata."
        try:
            if not meta:
                vectorstore = FAISS.from_texts(content, self.embedding)
            else:
                file_meta = {}
                for each in meta:
                    key, value = each.split(':')
                    file_meta[key] = value
                document = Document(
                    page_content=content,
                    metadata={file_meta},
                )
                vectorstore = FAISS.from_documents(document, self.embedding)
            if not Path(datastore / "index.faiss").exists():
                vectorstore.save_local(datastore)
            else:
                tmp_vectorstore = FAISS.from_documents(document, self.embedding)
                vectorstore.merge_from(tmp_vectorstore)
                vectorstore.save_local(datastore) 
            print(f"data saved to {datastore}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def add_doc_to_datastore(self, filename, meta: Dict = None, datastore="vectorstore"):
        #! add meta data add option
        "Adds files to datastore with optional metadata."
        try:
            doc = self.load_document(filename)
            vectorstore = FAISS.from_documents(doc, self.embedding)
            if not Path(datastore / "index.faiss").exists():
                vectorstore.save_local(datastore)
            else:
                tmp_vectorstore = FAISS.from_documents(doc, self.embedding)
                vectorstore.merge_from(tmp_vectorstore)
                vectorstore.save_local(datastore)
            print(f"Successfully added {filename} to the datastore.")
        except Exception as e:
            print(f"An error occurred: {e}")
    
    def chat(self, query, user):
        result = self.llm_chat.invoke(self.char_prompt.format(query=query))
        if self.llm_text == "openai":
            result = result.content

        result = f"""[Session Begin]
<<< S.A.F.E >>>
Welcome, Agent [{user}].

Request Received: [{query}]

Performing Clearance Verification...
Clearance Verified.

""" + result + """

Reminder: Ensure this information remains within Foundation parameters. Unauthorized dissemination is subject to immediate disciplinary action.
[Session End]
"""
        return result