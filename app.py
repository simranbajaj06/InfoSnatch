import os
import streamlit as st
import pickle
import time
from langchain import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.document_loaders import UnstructuredURLLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from secretKey import OPENAI_API_KEY
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

st.title("NewsBot : News Research Tool")
st.sidebar.title("News Articles URLs")

urls=[]
for i in range(3):
    url=st.sidebar.text_input(f"URL {i+1}")
    urls.append(url)

process_url_clicked=st.sidebar.button("Process URLs")
file_path="faiss_store_openai.pkl"

main_placeholder=st.empty()
llm=ChatOpenAI(temperature=0.8,max_tokens=500)

if process_url_clicked:
    # load data
    loader=UnstructuredURLLoader(urls=urls)
    main_placeholder.text("Data Loading Started ...")
    data=loader.load()
    # Split data
    text_splitter=RecursiveCharacterTextSplitter(separators=["\n\n","\n"," "],
                                                 chunk_size=1000,
                                                 chunk_overlap=200)
    main_placeholder.text("Text Splitter Started ...")
    docs=text_splitter.split_documents(data)
    #  Create openAI embeddings
    embeddings=OpenAIEmbeddings()
    vectorstore_openai=FAISS.from_documents(docs,embeddings)
    main_placeholder.text("Embeddings Vector Started Building ...")
    time.sleep(2)
    with open(file_path,"wb") as f:
        pickle.dump(vectorstore_openai,f)
    
query=main_placeholder.text_input("Query: ")
if query:
    if os.path.exists(file_path):
        with open(file_path,"rb") as f:
            vectorstore=pickle.load(f)
            chain=RetrievalQAWithSourcesChain.from_llm(llm=llm,retriever=vectorstore.as_retriever())
            result=chain({"question": query}, return_only_outputs=True)
            st.header("Answer")
            st.write(result["answer"])
            sources=result.get("sources","")
            if sources:
                st.subheader("Sources: ")
                sources_list=sources.split("\n")
                for source in sources_list:
                    st.write(source)




