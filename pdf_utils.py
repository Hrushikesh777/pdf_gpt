import pdftotext
from io import BytesIO
from langchain.text_splitter import MarkdownTextSplitter
import re
import unicodedata
import time
from fastapi.exceptions import HTTPException

from opeanai_utils import get_openai_embeddings
from storage import MarshalStorage

class PDFutil():
    def __init__(self) -> None:
        pass

    def process_pdf(self, filepath: str):
        """
        Process the PDF (split, get embeddings, store the embeddings)

        Parameters:
            filepath str: filepath of pdf
        
        Returns:
            dict: result with namespace, pages in pdf
        """
        try:
            with open(filepath, "rb") as fp:
                pages = pdftotext.PDF(fp)
        except Exception as e:
            raise HTTPException(
                status_code=422,
                detail=f"Not able able read file. Check if file is valid or currupted.",
            )

        text = ""
        for i in range(len(pages)):
            text += pages[i]
            text += "\n"

        texts = self._split_text(text)
        texts = self._clean_text(texts)
        embeddings, tokens = get_openai_embeddings(texts)
        print(f"Tokens used for pdf embeddings: [{tokens}]")
        namespace = self._get_namespace(filepath.split("/")[-1])

        data = []
        for text, emb in zip(texts, embeddings):
            data.append({
                "text": text,
                "emb": emb
            })

        mashal_storage = MarshalStorage(namespace)
        mashal_storage.ingest_data(namespace, data, len(pages))
        return {
            "message": "Done Processing",
            "total_pages": len(pages),
            "namespace": namespace
        }


    def _split_text(self, text):
        """
        Split text into small chunks

        Parameters:
            text str: text to be split
        
        Returns:
            list[str]: small text chunks
        """
        markdown_splitter = MarkdownTextSplitter(chunk_size=1000, chunk_overlap=50)
        docs = markdown_splitter.create_documents([text])
        text_data = [doc.page_content for doc in docs]
        return text_data

    def _clean_text(self, texts):
        """
        Clean the text: remove unicode, multiple spaces, tabs, newlines

        Parameters:
            texts list[str]: list of texts to be cleaned

        Returns:
            list[str]: list of cleaned texts
        """
        cleaned_docs = []

        for doc in texts:
            # convert unicode values to their original value
            clean_text = unicodedata.normalize('NFKD', doc.replace('\n', ' ').replace('\t', ' '))
            # remove unicode values that not possble to convet
            clean_text = re.sub(f'[^\x00-\x7F]+', ' ', clean_text)
            # convert multiple white spaces to single whitespace
            clean_text = re.sub(r'\s+', ' ', clean_text)
            cleaned_docs.append(clean_text.lower())

        return cleaned_docs

    def _get_namespace(self, text):
        """
        Get unique namespace form the filename and timestamp
        """
        # Remove all characters except alphanumeric and spaces
        text = re.sub(r"[^a-zA-Z0-9\s]+", " ", text).strip()
        # Convert multiple spaces into a single space
        text = re.sub(r'\s+', ' ', text)
        # Replace space with "-"
        text = re.sub(r'\s', '_', text)
        return f"book_{text}_{str(int(time.time()))}"

    @classmethod
    def get_top_matches(cls, question: str, marshal_storage: MarshalStorage):
        """
        Wrapper around get top matches from storage
        """
        return marshal_storage.get_top_matches(question)