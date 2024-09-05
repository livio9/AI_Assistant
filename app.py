import gradio as gr
import os
import re

from chat import chat, chat_stream
from pdf import generate_answer, generate_summary, generate_text
from function import function_calling
from search import search
from stt import audio2text
from tts import text2audio
from fetch import fetch
from mnist import image_classification
from image_generate import image_generate

messages = []
current_file_text = None

def add_text(history, text):
    global messages, current_file_text

    if text.startswith("/fetch "):
        url = re.search(r'^/fetch\s+(.*)', text).group(1)
        processed_results = fetch(url)
        user_input = {"role": "user",
                      "content": processed_results}
    else:
        user_input = {"role": "user", "content": text}

    messages.append(user_input)
    history = history + [(text, None)]

    if not text.startswith("/file"):
        current_file_text = None

    return history, gr.update(value="", interactive=False)

def add_file(history, file):
    global messages, current_file_text

    if file.name.endswith(".png"):
        current_file_text = file.name
        user_input = {"role": "user", "content": f"Please classify {current_file_text}"}
        messages.append(user_input)
        history = history + [((file.name,), None)]
        return history

    if file.name.endswith(".wav"):
        current_file_text = audio2text(file.name)
        prompt = current_file_text
    elif file.name.endswith(".txt"):
        with open(file.name, "r", encoding="utf-8") as f:
            current_file_text = f.read()
            prompt = generate_summary(current_file_text)

    user_input = {"role": "user", "content": prompt}
    messages.append(user_input)
    history = history + [((file.name,), None)]
    return history

def bot(history):
    global messages, current_file_text

    history[-1][1] = ""
    content = str(messages[-1]["content"])
    response = None

    if current_file_text is None:
        if content.startswith("/function"):
            messages[-1]["content"] = content[len("/function "):]
            response = function_calling(messages[-1:])
        elif content.startswith("/audio "):
            messages[-1]["content"] = content[len("/audio "):]
            response = chat(messages)
            audio_file_path = text2audio(response)
            history[-1][1] = (audio_file_path,)
        elif content.startswith("/search"):
            messages[-1]["content"] = search(content[8:].strip())
            response = chat_stream(messages)
        elif content.startswith("/image "):
            prompt = messages[-1]["content"][7:].strip()
            img_url = image_generate(prompt)
            response = img_url if img_url else "Sorry, I can't generate an image for you."
            history[-1][1] = (img_url,)
        else:
            response = chat_stream(messages)
    else:
        if content.startswith("/file"):
            messages[-1]["content"] = content[len("/file "):]
            messages[-1]["content"] = generate_answer(current_file_text, messages[-1]["content"])
            response = generate_text(messages[-1]["content"])
        elif current_file_text.endswith(".png"):
            response = image_classification(current_file_text)
        else:
            response = generate_text(messages[-1]["content"])

    if isinstance(history[-1][1], tuple):
        yield history
    elif isinstance(response, str):
        history[-1][1] += response
        yield history
    else:
        for event in response:
            if event["choices"][0]["delta"]:
                history[-1][1] += event["choices"][0]["delta"]["content"]
            yield history

    messages.append({"role": "assistant", "content": history[-1][1] if not isinstance(response, str) else response})

with gr.Blocks() as demo:
    chatbot = gr.Chatbot(
        [],
        elem_id="chatbot",
        avatar_images=(None, os.path.join(os.path.dirname(__file__), "avatar.png")),
    )

    with gr.Row():
        txt = gr.Textbox(
            scale=4,
            show_label=False,
            placeholder="Enter text and press enter, or upload an image",
            container=False,
        )
        clear_btn = gr.Button('Clear')
        btn = gr.UploadButton("📁", file_types=["image", "video", "audio", "text"])

    txt_msg = txt.submit(add_text, [chatbot, txt], [chatbot, txt], queue=False).then(
        bot, chatbot, chatbot
    )
    txt_msg.then(lambda: gr.update(interactive=True), None, [txt], queue=False)

    file_msg = btn.upload(add_file, [chatbot, btn], [chatbot], queue=False).then(
        bot, chatbot, chatbot
    )

    clear_btn.click(lambda: messages.clear(), None, chatbot, queue=False)

demo.queue()
demo.launch()