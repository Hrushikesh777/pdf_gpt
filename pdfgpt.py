import os
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed

from pdf_utils import PDFutil
from config import config
from storage import MarshalStorage
from opeanai_utils import merge_two_questions, get_answer_from_context

class PDFGPT:
    def __init__(self, namespaces: List[str] = [], top_k: int = 7) -> None:
        if not os.path.exists(config.marshal_storage_folder):
            os.makedirs(config.marshal_storage_folder)
        self.namespaces = namespaces
        self.top_k = top_k
        self.last_question = ""

    def add_pdf(self, filepath: str) -> dict:
        return PDFutil().process_pdf(filepath)
    
    def set_namespaces(self, namespaces: List[str]):
        self.namespaces = namespaces

    def get_all_namespaces(self):
        namespaces = []
        for item in os.listdir(os.path.join(os.getcwd(), config.marshal_storage_folder)):
            namespace = item.split("/")[-1][:-4]
            namespaces.append(namespace)

        return namespaces

    def _get_top_matches(self, merge_question: str, namespace: str):
        marshal_storage = MarshalStorage(namespace, load_data=True)
        top_matches_texts = PDFutil.get_top_matches(merge_question, marshal_storage)
        return top_matches_texts

    def rank_texts(self, merge_question: str):
        futures = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            for namespace in self.namespaces:
                future = executor.submit(self._get_top_matches, merge_question, namespace)
                futures.append(future)
            
        # Collect the results
        results = []
        for future in as_completed(futures):
            result = future.result()
            results.extend(result)

        # results = []
        # for namespace in self.namespaces:
        #     op = self._get_top_matches(merge_question, namespace)
        #     results.append(op)

        results = sorted(results, key=lambda x: x[1], reverse=True)
        results = [x[0] for x in results]
        # print(results)
        return results

    def answer_question(self, question: str):
        if len(self.namespaces) == 0:
            raise ValueError("0 namespace found. Set namespaces with set_namespaces() method.")
        merge_question = merge_two_questions(self.last_question, question)
        print(f"{merge_question=}")
        context = "\n".join(self.rank_texts(merge_question))
        res = get_answer_from_context(question, context, True)
        whole_response = ""
        for i, chunk in enumerate(res):
            data = chunk["choices"][0]["delta"].get("content", "")
            whole_response += data
            yield data

        self. last_question = merge_question
        # As of now not adding message to history TODO
        # marshal_storage.add_message(merge_question, question, whole_response)