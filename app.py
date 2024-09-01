import gradio as gr
import os
import time

from chat import chat, chat_stream
from search import search
from pdf import generate_summary, generate_answer, generate_text
from function import function_calling
# Chatbot demo with multimodal input (text, markdown, LaTeX, code blocks, image, audio, & video). Plus shows support for streaming text.

messages = []
current_file_text = None

def add_text(history, text):
    global messages
    user_input = {"role": "user", "content": text}
    messages.append(user_input)
    history = history + [(text, None)]
    return history, gr.update(value="", interactive=False)



def add_file(history, file):
    """
    TODO
    """
    global messages
    global current_file_text
    if file.name.endswith(".txt"):
        with open(file.name, "r", encoding="utf-8") as f:
            current_file_text = f.read()
            prompt = generate_summary(current_file_text)

    user_input = {"role": "user", "content": prompt}
    messages.append(user_input)
    history = history + [((file.name,), None)]
    return history


def bot(history):
    # 普通聊天模式
    # global messages
    # # 调用 chat 函数生成回复
    # assistant_reply = chat(messages)
    
    # # 更新 history 中最后一条记录的 AI 回复部分
    # history[-1][1] = assistant_reply
    
    # # 记录新的 assistant 回复到 messages 中
    # messages.append({"role": "assistant", "content": assistant_reply})
    
    # return history

    # 流式聊天模式
    global messages
    content = messages[-1]["content"]
    assistant_reply_stream = None
    
    if content.startswith("/search"):
        # 提取 /search 指令后的内容
        search_query = content[len("/search "):]
        
        # 调用 search 函数获取搜索结果
        search_result = search(search_query)
        
        # 将搜索结果更新到 messages 中
        messages.append({"role": "user", "content": search_result}) 
        
    elif content.startswith("Summarize the following text:"):
        print("Summarize the following text:")
        assistant_reply_stream = generate_text(content)
    
    elif content.startswith("/file"):
        print("/file")
        # 提取 /file 指令后的内容
        file_content = content[len("/file "):]
        
        # 调用 generate_answer 函数生成问题
        question = generate_answer(current_file_text, file_content)
        print(question)
        
        # 将问题更新到 messages 中
        messages[-1]["content"] = question
    
    elif content.startswith("/function"):
        print("/function")
        # 提取 /function 指令后的内容
        function_content = content[len("/function "):]
        
        # 将功能执行结果更新到 messages 中
        messages[-1]["content"] = function_content

        assistant_reply_stream = function_calling(messages)
    
    if(assistant_reply_stream == None):
        # 使用 chat_stream 函数生成流式回复
        assistant_reply_stream = chat_stream(messages)
    
    print("type:", type(assistant_reply_stream))
    
    if isinstance(assistant_reply_stream, str):
        history[-1][1] = assistant_reply_stream
        yield history
    else:
        assistant_reply = ""
        for chunk in assistant_reply_stream:
            assistant_reply += chunk["choices"][0]["delta"].get("content", "")
            history[-1][1] = assistant_reply
            yield history
    
    # 记录完整的 assistant 回复到 messages 中
    if isinstance(assistant_reply_stream, str):
        messages.append({"role": "assistant", "content": assistant_reply_stream})
    else:
        messages.append({"role": "assistant", "content": assistant_reply})

with gr.Blocks() as demo:
    chatbot = gr.Chatbot(
        [],
        elem_id="chatbot",
        avatar_images=(None, (os.path.join(os.path.dirname(__file__), "avatar.png"))),
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