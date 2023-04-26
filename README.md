# Docbot App for Nexodus LLM/NLP Docs POC

https://user-images.githubusercontent.com/1711674/234722846-914445e6-12d9-464c-a556-63e4906575f5.mov

### Docbot Pre-Requisites

- [Python](https://www.python.org/downloads/)
- [Flask](https://pypi.org/project/Flask/)

```commandline
python3 -m venv env
source env/bin/activate
pip install -U flask
```

- LLM modules

```commandline
pip install flask langchain requests sentence-transformers chromadb openai

```

Add your OpenAI key in `docbot.py`. Get a key from [OpenAI](https://platform.openai.com/account/api-keys).

```python
os.environ["HUGGINGFACEHUB_API_TOKEN"] = "insert_your_key_here"
```

Add a username/password to `docbot.py`

```python
users = {
    "username": generate_password_hash("password")
}
```
### Run

Run the app with `python3 docbot` which starts the flask server running the web UI.

```commandline
$ git clone https://github.com/nerdalert/docbot-nexodus.git
$ python3 docbot.py
 * Serving Flask app 'docbot'
 * Debug mode: on
INFO:werkzeug:WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.1.203:5000
INFO:werkzeug:Press CTRL+C to quit
```

### Docbot Usage

Add the markdown file URLs you want to add to the search into urls.txt file. You can use the following tool to scrape your repo [markdown-url-extractor](https://github.com/nerdalert/markdown-url-extractor).
The markdown files are stored in the `data` directory and the vector database is stored in `chroma_db_store` automatically. They files are chunked and embedded for a similarity search before getting shipped to OpenAI.

Open the page and chat with the docbot http://127.0.0.1:8080 or your machines routable address.

### Some Nerdy Details

This Python code is an implementation of a Flask web application that uses the langchain library to perform question answering using a pre-trained language model from OpenAI.

The code begins with importing necessary libraries such as os, requests, Flask, render_template, request, and jsonify. Then, it defines a Flask application object and loads URLs from a file named "urls.txt". It filters the URLs that do not start with the given string, retrieves the content of each URL and saves it as a text file. It then loads each text file using the TextLoader class from the langchain library, adds the URL as metadata to each document, and splits the documents into chunks using the CharacterTextSplitter class.

The next step is to extract embeddings from the document chunks using the OpenAIEmbeddings class, and store the embeddings in a Chroma vector store using the Chroma class from the langchain library. Alternatively, you can make the Chroma DB persistent by uncommenting and replacing the corresponding line.

The Python code then loads a pre-trained language model using OpenAI, and creates a question answering chain using the load_qa_chain function from the langchain library.

The send_click function performs a similarity search using the input prompt and the Chroma vector store. It returns an error message if no relevant documents are found. Otherwise, it uses the pre-trained language model to find the best answer to the question based on the documents retrieved from the similarity search.

Finally, the Flask app is configured with two routes - "/" and "/query". The index_page function renders an HTML template, while the query function handles POST requests containing a prompt. It passes the prompt to the send_click function and returns the best answer and source URL as a formatted response.

The application can be run by calling python docbot.py in the terminal. It will listen on port 8080 and will be accessible via a web browser at http://localhost:8080/.
