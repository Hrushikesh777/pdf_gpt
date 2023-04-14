import gradio as gr
import random
import time

from pdfgpt import PDFGPT

pdf_gpt = PDFGPT()

with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column(scale=0.3):
            file = gr.File(label="PDF File")
            upload_file = gr.Button(value="Upload File")
            gr.Markdown("<h4 style='text-align: center'>OR</h4>")
            namespaces = gr.Dropdown(choices=pdf_gpt.get_all_namespaces(), value=[], multiselect=True, label="Namespaces", info="Select one or more namespaces.")
            gr.Markdown("<hr style='border: 1px solid black'>")
            err_msg = gr.Textbox(label="Error messages", placeholder="Any error messages will display here..")
            clear = gr.Button(value="Clear ALL")

        with gr.Column(scale=0.7):
            chatbot = gr.Chatbot(label="Chatbot").style(height=400)
            msg = gr.Textbox(label="Question", placeholder="Ask question..")
            submit_btn = gr.Button(value="Submit")

    def add_pdf(file, err_msg):
        try:
            filepath = file.name
            op = pdf_gpt.add_pdf(filepath)
            namespace = op["namespace"]
            return gr.Dropdown.update(choices=pdf_gpt.get_all_namespaces(), value=[namespace]), err_msg
        except Exception as e:
            err_msg = str(e)
            return namespaces, err_msg

    def user(user_message, history, err_msg):
        if not user_message:
            err_msg = "Question should not be empty."
            return "", history, err_msg
        return "", history + [[user_message, ""]], err_msg

    def bot(history, namespaces, err_msg):
        if len(namespaces) == 0:
            err_msg = "Select one or more namespaces."
            return history, err_msg

        try:
            question = history[-1][0]
            pdf_gpt.set_namespaces(namespaces)
            # question = "what is gst"
            for val in pdf_gpt.answer_question(question):
                # print(val, end="", flush=True)
                history[-1][1] += val
                yield history, err_msg
        except Exception as e:
            err_msg = str(e)
            return history, err_msg

    msg.submit(user, [msg, chatbot, err_msg], [msg, chatbot, err_msg], queue=False).then(
        bot, [chatbot, namespaces, err_msg], [chatbot, err_msg]
    )
    submit_btn.click(user, [msg, chatbot, err_msg], [msg, chatbot, err_msg], queue=False).then(
        bot, [chatbot, namespaces, err_msg], [chatbot, err_msg]
    )
    clear.click(lambda: None, None, chatbot, queue=False)
    upload_file.click(add_pdf, [file, err_msg], [namespaces, err_msg])

demo.queue()
demo.launch()
