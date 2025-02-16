from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_core.documents import Document
from langchain_chroma import Chroma

from src.entities.pokemon_place import PokemonPlace

import uuid
import os
import json


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=510,
    chunk_overlap=50,
    length_function=len,
    separators=['\n', '.', '\n\n']
)


embeddings_generator = OllamaEmbeddings(
    model='mxbai-embed-large:latest'
)

chroma_db_path = './database/chromadb'

vector_store = Chroma(
    persist_directory=chroma_db_path,
    embedding_function=embeddings_generator,
    collection_name='pokemon'
)

pokemon_places_path = './database/places'

for filename in os.listdir(pokemon_places_path):
    json_path = f'{pokemon_places_path}/{filename}'

    with open(json_path, 'r') as file:
        pokemon_place_json = json.load(file)

        pokemon_place = PokemonPlace.from_dict(pokemon_place_json)

        description_chunks = text_splitter.split_text(
            pokemon_place.description)

        langchain_documents = [
            Document(
                page_content=chunk,
                id=str(uuid.uuid4()),
                metadata={
                    'place_name': pokemon_place.name,
                    'region': pokemon_place.region,
                    'generation': pokemon_place.generation,
                    'source_url': pokemon_place.url,
                    'image_src': pokemon_place.image_src
                }
            ) for chunk in description_chunks
        ]

        vector_store.add_documents(langchain_documents)
        print(
            f'Added {len(langchain_documents)} documents about {pokemon_place.name} to vector store (chromadb)')
