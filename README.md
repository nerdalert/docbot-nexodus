# Docbot App for Nexodus LLM/NLP Docs POC

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
pip install flask langchain requests sentence-transformers chromadb

```

Add your HuggingFaceHub key in `docbot.py`. Get a key from [OpenAI](https://platform.openai.com/account/api-keys). You get $5 free in API usage from OpenAI. If you upload a small file like the example, `gpt-3.5-turbo` model is doesn't incur much if any cost. GAI competition should drive small usage to zero.

```python
os.environ["HUGGINGFACEHUB_API_TOKEN"] = "insert_your_key_here"
```

### Run

Run the app with `python3 docbot-hugging.py` which starts the flask server running the web UI.

```commandline
$ git clone https://github.com/nerdalert/docbot-nexodus.git
$ python3 docbot-hugging.py
 * Serving Flask app 'docbot'
 * Debug mode: on
INFO:werkzeug:WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.1.203:5000
INFO:werkzeug:Press CTRL+C to quit
```

### Docbot Usage

Open the page and chat with the docbot. The markdown files are stored in the root directory as txt. They are chunked and embedded to the model via HuggingFace. OpenAI GPT-3.5 is much better and faster, but huggingface is free :hugs:


### Some Nerdy Details

This Python code is an implementation of a Flask web application that uses the langchain library to perform question answering using a pre-trained language model from HuggingFace Hub.

The code begins with importing necessary libraries such as os, requests, Flask, render_template, request, and jsonify. Then, it defines a Flask application object and loads URLs from a file named "urls.txt". It filters the URLs that do not start with the given string, retrieves the content of each URL and saves it as a text file. It then loads each text file using the TextLoader class from the langchain library, adds the URL as metadata to each document, and splits the documents into chunks using the CharacterTextSplitter class.

The next step is to extract embeddings from the document chunks using the HuggingFaceEmbeddings class, and store the embeddings in a Chroma vector store using the Chroma class from the langchain library. Alternatively, you can make the Chroma DB persistent by uncommenting and replacing the corresponding line.

The Python code then loads a pre-trained language model using HuggingFaceHub, and creates a question answering chain using the load_qa_chain function from the langchain library.

The send_click function performs a similarity search using the input prompt and the Chroma vector store. It returns an error message if no relevant documents are found. Otherwise, it uses the pre-trained language model to find the best answer to the question based on the documents retrieved from the similarity search.

Finally, the Flask app is configured with two routes - "/" and "/query". The index_page function renders an HTML template, while the query function handles POST requests containing a prompt. It passes the prompt to the send_click function and returns the best answer and source URL as a formatted response.

The application can be run by calling python docbot-hugging.py in the terminal. It will listen on port 8080 and will be accessible via a web browser at http://localhost:8080/.