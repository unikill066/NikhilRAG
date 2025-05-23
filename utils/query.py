#!/usr/bin/env python3

import argparse, os, sys
from dotenv import load_dotenv
# from dataclasses import dataclass
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
import constants

load_dotenv()

CHROMA_PATH = str(constants.CHROMA_DB_PATH)

PROMPT_TEMPLATE = """
Answer the question based only on the following context:
{context}
---
Answer the question based on the above context: {question}
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text

    embedding_function = OpenAIEmbeddings(model=constants.MODEL)
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    results = db.similarity_search_with_relevance_scores(query_text, k=3)
    if len(results) == 0 or results[0][1] < 0.7:
        print(f"Unable to find matching results.")
        return

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    print(prompt)

    model = ChatOpenAI(model='gpt-3.5-turbo')
    response_text = model.predict(prompt)

    sources = [doc.metadata.get("source", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)


if __name__ == "__main__":
    main()


# from langchain_openai import OpenAIEmbeddings
# from langchain.evaluation import load_evaluator
# from dotenv import load_dotenv
# import os, sys, openai


# parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(parent_dir)
# import constants

# load_dotenv()

# def main():
#     # Get embedding for a word.
#     embedding_function = OpenAIEmbeddings(model=constants.MODEL)
#     vector = embedding_function.embed_query("apple")
#     print(f"Vector for 'apple': {vector}")
#     print(f"Vector length: {len(vector)}")

#     # Compare vector of two words
#     evaluator = load_evaluator("pairwise_embedding_distance")
#     words = ("apple", "iphone")
#     x = evaluator.evaluate_string_pairs(prediction=words[0], prediction_b=words[1])
#     print(f"Comparing ({words[0]}, {words[1]}): {x}")


# if __name__ == "__main__":
#     main()