from pydantic import BaseModel

class AppConfig(BaseModel):
    # openapi
    openai_api_key = "your_api_key"

    # gpt model
    gpt_model = "gpt-3.5-turbo"
    
    # book metadata question
    book_metadata_question = "Introduction, author, decription, summary, content, index"

    # supported filtypes
    supported_filetypes = ["pdf"]

    # marshal storage folder
    marshal_storage_folder = "marshal_storage"

    # max file size 20MB
    size_in_mb = 20
    max_file_size_bytes = size_in_mb * 1000000

    # context answer prompt filename
    context_answer_prompt_filename = "context_answers_prompt.txt"

    # question merge prompt filename
    question_merge_prompt_filename = "question_merge.txt"

config = AppConfig()