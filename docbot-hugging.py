import os
import requests
from flask import Flask, render_template, request, jsonify
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains.question_answering import load_qa_chain
from langchain import HuggingFaceHub

app = Flask(__name__)

# Set the HuggingFace Hub API token as an environment variable
os.environ["HUGGINGFACEHUB_API_TOKEN"] = "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"

# Chroma persistance directory
directory = "db"

# Create the directory if it doesn't exist
if not os.path.exists(directory):
    os.makedirs(directory)

# Function to load URLs from a text file
def load_urls_from_file(filename):
    with open(filename, "r") as f:
        # Filter out any URLs that don't start with the given string
        urls = [url.strip() for url in f.readlines() if
                url.strip().startswith("https://raw.githubusercontent.com/nexodus-io/nexodus/main/docs/")]
    return urls


# Load and cache index
document_urls = load_urls_from_file("urls.txt")
print(document_urls)

documents = []
for url in document_urls:
    res = requests.get(url)
    filename = url.split("/")[-1].replace(".md", ".txt")
    with open(filename, "w") as f:
        f.write(res.text)

    loader = TextLoader(filename)
    doc = loader.load()
    for d in doc:
        d.metadata["url"] = url  # Add the url to the metadata
    documents.extend(doc)

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

embeddings = HuggingFaceEmbeddings()
# Uncomment and replace the above line to make Chroma DB transient
# db = Chroma.from_documents(docs, embeddings)
db = Chroma.from_documents(docs, embeddings, persist_directory=directory)

llm = HuggingFaceHub(repo_id="google/flan-t5-xl", model_kwargs={"temperature": 0, "max_length": 512})
chain = load_qa_chain(llm, chain_type="stuff")


def send_click(prompt):
    docs = db.similarity_search(prompt)
    if not docs:
        return "No relevant documents found."

    answers = []
    sources = []
    for doc in docs:
        output = chain.run(input_documents=[doc], question=prompt)
        answers.append(output)
        raw_url = doc.metadata.get("url", "unknown source")

        # Replace the first part of the raw URL with "https://docs.nexodus.io/"
        fixed_url = raw_url.replace("https://raw.githubusercontent.com/nexodus-io/nexodus/main/docs/",
                                    "https://docs.nexodus.io/")

        # Strip off ".md" from the URL if it ends in ".md"
        if fixed_url.endswith(".md"):
            fixed_url = fixed_url.rstrip(".md")

        sources.append(fixed_url)

    # Assuming that the answer with the highest confidence is the first one in the list
    best_answer = answers[0]
    best_source = sources[0]

    # Check for a 500 response and return an error message to the user
    if best_answer == 500:
        return "Oops! Something went wrong with the HuggingFace Hub API. Please try again later."

    return {"answer": best_answer, "source": best_source}


@app.route("/")
def index_page():
    return render_template("index.html")


@app.route("/query", methods=["POST"])
def query():
    data = request.get_json()
    prompt = data["prompt"]
    response = send_click(prompt)
    formatted_response = f"{response['answer']} (<a href='{response['source']}' target='_blank'>Source</a>)"
    return jsonify({"response": formatted_response})


if __name__ == "__main__":
    app.run(debug=False, port=8080, host='0.0.0.0')
