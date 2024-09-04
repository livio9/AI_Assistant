import gradio as gr
import os
import time
from image_generate import image_generate
from mnist import image_classification
from chat import chat, chat_stream
from search import search
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
    global messages
    global current_file_text
    if file.name.endswith(".png"):
        current_file_text = file.name
        classify_query = f"Please classify{current_file_text}"
        messages.append({"role": "user", "content": classify_query})

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

    # 标记是否流式输出
    flu = 1

    # 流式聊天模式
    global messages
    if current_file_text is None:
        content = messages[-1]["content"]

        if content.startswith("/search"):
            # 提取 /search 指令后的内容
            search_query = content[len("/search "):]

            # 调用 search 函数获取搜索结果
            search_result = search(search_query)

            # 将搜索结果更新到 messages 中
            messages.append({"role": "user", "content": search_result})

        # 生成图像功能（YUNYAN ZHAO）
        elif content.startswith("/image"):
            flu = 0
            img_query = content[len("/image "):]
            messages.append({"role": "user", "content": content})
            img_link = image_generate(img_query)
            messages.append({"role": "assistant", "content": f'<img src="{str(img_link)}" alt="Generated Image">'})
            # messages.append({"role": "assistant", "content": str(history[-1][1][0])})
            history[-1][1] = (img_link,)
            yield history

        # 使用 chat_stream 函数生成流式回复
        if flu:
            assistant_reply_stream = chat_stream(messages)
            assistant_reply = ""
            for chunk in assistant_reply_stream:
                assistant_reply += chunk["choices"][0]["delta"].get("content", "")
                history[-1][1] = assistant_reply
                yield history

            # 记录完整的 assistant 回复到 messages 中
            messages.append({"role": "assistant", "content": assistant_reply})
    elif current_file_text.endswith(".png"):
        # print(current_file_text)
        reply_classify = image_classification(current_file_text)
        history[-1][1] = reply_classify
        yield history
        messages.append({"role": "assistant", "content": reply_classify})


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
