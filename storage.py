from typing import List
import os
import marshal
from scipy.spatial.distance import cosine
import numpy as np
import time

from config import config
from opeanai_utils import (
    get_openai_embedding_question, 
    get_answer_from_context
    )

class MarshalStorage():
    """
    Marshal Storage class using inbuilt python package for storage of embeddings and questions
    """
    def __init__(self, namespace, top_k: int = 7, load_data = False) -> None:
        """
        Init method for marshal storage class.

        Parameters:
            namespace [str]: unique namespace for each book
            docs optional[list[dict]]: list of dictionary with texts and embeddings
            top_k optional[int]: number of results to be fetch that are closest to question
            pdf_pages optional[int]: total pages in book
        """
        self.namespace = namespace
        self.top_k = 7
        self.filename = os.path.join(os.getcwd(), config.marshal_storage_folder, f"{namespace}.bin")
        print(self.filename)
        if load_data:
            self.read_data()
        
    def ingest_data(self, namespace, docs, pdf_pages):
        """
        Ingest docs.

        Parameters:
            namespace [str]: unique namespace for each book
            docs optional[list[dict]]: list of dictionary with texts and embeddings
            pdf_pages optional[int]: total pages in book
        """
        try:
            self.data = {
                    namespace:{
                        "namespace": namespace,
                        "total_messages": 0,
                        "messages": [],
                        "docs": docs,
                        "docs_len": len(docs)
                    }
                }
            question = f"Explain in very detail. Extract {config.book_metadata_question} from context. If not possible just say 'no information'"
            context = "\n".join([x[0] for x in self.get_top_matches(question)])
            response = get_answer_from_context(question, context, False)
            response = response["choices"][0]["message"]["content"]
            response_emb = get_openai_embedding_question(response)
            if response and response_emb:
                self.data[self.namespace]["docs"].append({
                    "text": f"Information related to {config.book_metadata_question} from context. {response}. The book has total {pdf_pages} pages.",
                    "emb": response_emb
                })
                self.data[self.namespace]["docs_len"] += 1
                # This will write data, so no need to write again
                # self.add_message("", response)
            self.write_data()
        except Exception as e:
            print(f"Error occured while ingesting book docs. Namespace: [{self.namespace}]\n{e}")


    def read_data(self):
        """
        read data from binary file
        """
        try:
            with open(self.filename, "rb") as fp:
                self.data = marshal.load(fp)
                print(f"Data Loaded Successfully.")
        except Exception as e:
            print(f"Invalid filename provided. [{self.filename}]")

    def write_data(self):
        """
        write data from binary file
        """

        with open(self.filename, "wb") as fp:
            marshal.dump(self.data, fp)

    def add_message(self, question, original_question, answer):
        """
        add message in the namespace

        Parameters:
            question str: question asked by user
            answer str: answer provide by system
        """

        self.data[self.namespace]["messages"].append({
                "time": str(time.time()),
                "question": question,
                "original_question": original_question,
                "answer": answer
            })
        self.data[self.namespace]["total_messages"] += 1
        self.write_data()

    def get_top_matches(self, question):
        """
        get top texts matching with question

        Parameters:
            question str: question asked by user

        Returns:
            top_matches list[str]: top texts similar to question
        """

        question_emb = np.array(get_openai_embedding_question(question))
        docs = self.data[self.namespace].get("docs", [])
        doc_embeddings = np.array([x["emb"] for x in docs])

        similarity_scores = np.apply_along_axis(lambda emb: 1 - cosine(question_emb, emb), axis=1, arr=doc_embeddings)
        most_similar_indices = np.argsort(-similarity_scores)[:self.top_k]

        top_matches = [[docs[x]["text"], similarity_scores[x]] for x in most_similar_indices]
        return top_matches
    
    def get_last_question(self):
        """
        Get last question from conversation history
        """
        messages = self.data[self.namespace].get("messages",[{}])
        last_question = ""
        try:
            last_question = messages[-1].get("question", "")
        except:
            pass
        return last_question
    