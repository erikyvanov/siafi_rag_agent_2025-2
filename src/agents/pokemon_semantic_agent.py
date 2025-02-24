from langchain.vectorstores import VectorStore
from langchain_core.prompts import PromptTemplate


_PROMP = PromptTemplate.from_template("""
    Eres un experto en el mundo pokemon.
    Utilice los siguientes elementos del contexto recuperado para responder a la pregunta
    No es necesario que le digas al usuario que de acierdo a la informacion recuperada. Se natural
    Los documentos tiene metadatos. Usalos para construir la respuesta.
    No combines la informacion de los docuemntos.
    Agrega uno que otro emoji para mejorar la respuesta
    La respuesta debe estar en formato markdown.
                                      
    Los docuemntos pueden contener .image_src. Si es el caso imprime la imagen en formato markdown                           
                                                                                          
    Pregunta: {question}
    Contexto: {context}
                                      
    Respuesta:
""")


class PokemonSemanticAgent:
    def __init__(self, vector_store: VectorStore, llm):
        self.vector_store = vector_store
        self.llm = llm

    def generate(self, question: str, k: int):
        similarity_results = self.vector_store.similarity_search(question, k)
        prompt_with_context = _PROMP.invoke(
            {
                'question': question,
                'context': similarity_results
            }
        )

        return self.llm.invoke(prompt_with_context)
    
    def generate_stream(self, question: str, k: int):
        similarity_results = self.vector_store.similarity_search(question, k)
        prompt_with_context = _PROMP.invoke(
            {
                'question': question,
                'context': similarity_results
            }
        )

        return self.llm.stream(prompt_with_context)

