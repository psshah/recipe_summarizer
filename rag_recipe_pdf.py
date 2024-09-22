# Import necessary libraries
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core import Settings
from llama_index.core.callbacks import CallbackManager
from langfuse.llama_index import LlamaIndexCallbackHandler

# Load environment variables
load_dotenv()

# Set up tracing
langfuse_callback_handler = LlamaIndexCallbackHandler()
Settings.callback_manager = CallbackManager([langfuse_callback_handler])

# Load documents from a directory (you can change this path as needed)
documents = SimpleDirectoryReader("data").load_data()

print(f"Number of documents: {len(documents)}")

# Create an index from the documents
index = VectorStoreIndex.from_documents(documents)

# Create a query engine
query_engine = index.as_query_engine()

# Example query
response = query_engine.query("What ingredients do I need for kofta?")
langfuse_callback_handler.flush()

print(response)
