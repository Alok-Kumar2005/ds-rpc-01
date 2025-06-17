from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from llm_config import groq_model
import os
from dotenv import load_dotenv

load_dotenv()

def llm_model(
    prompt_template: PromptTemplate,
    model_name: str = groq_model,
    temperature: float = 0.5,
    **inputs
) -> str:
    """
    Build and run a ChatGroq chain with any number of inputs.

    Args:
      prompt_template: a langchain.PromptTemplate 
      model_name:      name of your GROQ model (default from llm_config)
      temperature:     sampling temperature
      **inputs:        keyword args for each template variable

    Returns:
      The model’s text response.
    """
    llm = ChatGroq(
        model=model_name,
        temperature=temperature,
        api_key=os.getenv("GROQ_API_KEY"),
    )
    chain = prompt_template | llm
    return chain.invoke(inputs)


# static = PromptTemplate(
#     input_variables=[],
#     template="Give me a haiku about autumn."
# )

# poem = llm_model(static)
# print(poem)
