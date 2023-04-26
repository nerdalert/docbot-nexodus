import os
import requests
from flask import Flask, render_template, request, jsonify
from flask_httpauth import HTTPBasicAuth
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import UnstructuredMarkdownLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

auth = HTTPBasicAuth()
# Define the user and password hash
users = {
    "username": generate_password_hash("password")
}


@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username


# Set OpenAI API key
os.environ["OPENAI_API_KEY"] = "<INSERT_OPENAI_API_KEY>"

# Define the data directory
data_directory = "data"

# Create the data directory if it doesn't exist
if not os.path.exists(data_directory):
    os.makedirs(data_directory)

# Chroma persistance directory
chroma_persist_directory = "chroma_db_store/"

# Create the directory if it doesn't exist
if not os.path.exists(chroma_persist_directory):
    os.makedirs(chroma_persist_directory)


# Function to load URLs from a text file
def load_urls_from_file(filename):
    with open(filename, "r") as f:
        urls = [url.strip() for url in f.readlines() if
                url.strip().startswith("https://raw.githubusercontent.com/nexodus-io/nexodus/main/docs/")]
    return urls


# Load and cache index
document_urls = load_urls_from_file("urls.txt")
print(document_urls)

# Download and save documents from the URLs
documents = []
for url in document_urls:
    res = requests.get(url)
    filename = os.path.join(data_directory, url.split("/")[-1])
    with open(filename, "w") as f:
        f.write(res.text)

    loader = UnstructuredMarkdownLoader(filename)
    doc = loader.load()
    for d in doc:
        d.metadata["url"] = url  # Add the url to the metadata
    documents.extend(doc)

# Split the documents into smaller chunks
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

# Initialize embeddings and Chroma database
embeddings = OpenAIEmbeddings()
db = Chroma.from_documents(docs, embeddings, persist_directory=chroma_persist_directory)


# Function to send a query and return the response
def send_click(prompt):
    print("Debug: sending query")
    qna = RetrievalQA.from_chain_type(ChatOpenAI(temperature=0.5, model_name="gpt-3.5-turbo"), chain_type="stuff", retriever=db.as_retriever())

    answer = qna.run(prompt)
    print("Debug: received answer")

    docs = db.similarity_search(prompt)
    if not docs:
        return "No relevant documents found."

    raw_source = docs[0].metadata["url"]

    # Replace the first part of the raw URL with "https://docs.nexodus.io/"
    source = raw_source.replace("https://raw.githubusercontent.com/nexodus-io/nexodus/main/docs/",
                                "https://docs.nexodus.io/")

    # Strip off ".md" from the URL if it ends in ".md"
    if source.endswith(".md"):
        source = source.rstrip(".md")

    print(source)

    # return output
    return {"answer": answer, "source": source}


# Define routes for the Flask app
@app.route("/")
@auth.login_required
def index_page():
    return render_template("index.html")


@app.route("/query", methods=["POST"])
@auth.login_required
def query():
    data = request.get_json()
    prompt = data["prompt"]
    response = send_click(prompt)
    formatted_response = f"<table style='width: 100%;'><tr><td style='vertical-align: top;'>{response['answer']}</td></tr><tr><td style='vertical-align: bottom;'><a href='{response['source']}' target='_blank'>Source</a></td></tr></table>"

    return jsonify({"response": formatted_response})


if __name__ == "__main__":
    app.run(debug=False, port=8080, host='0.0.0.0')
    # app.run(debug=True)
