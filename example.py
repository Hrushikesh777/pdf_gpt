from pdfgpt import PDFGPT

def run():
    pdf_gpt = PDFGPT()
    # filepath = "/Users/hrushikeshvanga/Documents/rushi/without_fastapi/India GST.pdf"
    # op = pdf_gpt.add_pdf(filepath)
    # namespace = op["namespace"]
    # print(namespace)
    namespace = "book_India_GST_pdf_1681286104"
    pdf_gpt.set_namespaces([namespace])
    question = "what is gst"
    for val in pdf_gpt.answer_question(question):
        print(val, end="", flush=True)

    question = "what explain in simple terms"
    for val in pdf_gpt.answer_question(question):
        print(val, end="", flush=True)

    # print(pdf_gpt.get_all_namespaces())

if __name__ == "__main__":
    run()
