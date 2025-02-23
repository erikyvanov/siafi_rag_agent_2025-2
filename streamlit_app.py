import streamlit as st

from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv

from src.agents.pokemon_semantic_agent import PokemonSemanticAgent


HUMAN = "HUMAN"
AI = "AI"


class StreamlitUI:
    def __init__(self):
        load_dotenv('.env')
        self.__init_semantic_agent()


    def __init_semantic_agent(self):
        if "semantic_agent" not in st.session_state:

            deep_seek_llm = ChatOpenAI(
                model='gpt-4-turbo',
            )
            embeddings_generator = OllamaEmbeddings(
                model='mxbai-embed-large'
            )

            vector_store = Chroma(
                collection_name='pokemon',
                embedding_function=embeddings_generator,
                persist_directory='./database/chromadb'
            )

            agent = PokemonSemanticAgent(
                vector_store,
                deep_seek_llm
            )

            st.session_state.semantic_agent = agent

    def display_sidebar(self):
        st.sidebar.image('./assets/siafi-logo-blanco.webp', use_container_width=True)

        st.sidebar.title("⚡ Pokemon Expert Agent")

        st.sidebar.markdown(
            """
            Este proyecto forma parte de la iniciativa **Proyectos de Crecimiento** de la sociedad SIAFI UNAM
            """
        )

        st.sidebar.markdown("Autor: **Erik Ivanov Dominguez**")

    def display_chat_history(self):
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message['type']):
                st.markdown(message["content"])


    def handle_human_message(self, message: str):
        st.chat_message(HUMAN).markdown(message)

        st.session_state.messages.append(
            {
                "type": HUMAN,
                "content": message
            }
        )

    def handle_ai_message(self, prompt: str):
        agent = st.session_state.semantic_agent
        response = agent.generate_stream(prompt, 5)

        with st.chat_message(AI):
            chat_response = st.write_stream(response)

        st.session_state.messages.append(
            {
                "type": AI,
                "content": chat_response
            }
        )

    def run(self):
        st.title("Pokemon Expert Agent")
        self.display_sidebar()

        self.display_chat_history()

        prompt = st.chat_input("Mensaje a Pokemon Expert Agent")
        if prompt:
            self.handle_human_message(prompt)
            self.handle_ai_message(prompt)


if __name__ == "__main__":
    ui = StreamlitUI()
    ui.run()