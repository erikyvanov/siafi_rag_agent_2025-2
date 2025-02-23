from langchain_chroma import Chroma

from langchain_ollama import OllamaEmbeddings
from langchain_openai import ChatOpenAI
import os

from dotenv import load_dotenv

from src.agents.pokemon_semantic_agent import PokemonSemanticAgent

load_dotenv('.env')


deep_seek_llm = ChatOpenAI(
    model='deepseek-chat',
    base_url='https://api.deepseek.com',
    api_key=os.getenv('DEEP_SEEK_API_KEY')
)

embeddings_generator = OllamaEmbeddings(
    model='mxbai-embed-large'
)

question = 'Cuentame algo magico con muchas flores y vegetacion'

vector_store = Chroma(
    collection_name='pokemon',
    embedding_function=embeddings_generator,
    persist_directory='./database/chromadb'
)

agent = PokemonSemanticAgent(
    vector_store,
    deep_seek_llm
)

response = agent.generate_stream(question, 5)

for token in response:
    print(token.content, end='')
