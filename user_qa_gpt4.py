import streamlit as st
import openai 
import time
import tiktoken # This model's maximum context length is 16385 tokens. However, your messages resulted in 21621 tokens. 

####d
'''
This is a smart assistant demo II for https://www.moj.go.jp/isa/
Have a great day! 😊
\nこれは Pony が作成したスマートアシスタントのデモです。素敵な一日をお過ごしください！😊
\nPony AI
'''

# calculate token
def truncate_text(text, max_tokens=6000):
    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
    tokens = enc.encode(text)
    truncated_text = enc.decode(tokens[:max_tokens])
    return truncated_text


# calculate messages token
def count_tokens(messages):
    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
    return sum(len(enc.encode(m["content"])) for m in messages)

# 设定最大 token 限制（确保留有足够空间）
MAX_TOKENS = 16000



# Function to switch language
def switch_language(lang):
    return lang == "日本語"

# Add the language switch button in the sidebar
with st.sidebar:
    st.title("User View")
    language = st.radio("Language", ("English", "日本語"), index=0)
    openai_api_key = st.text_input("OpenAI API Key", key="file_qa_api_key", type="password")
    
    "[[About](support@pony.com)](© 2024 Pony. All rights reserved.)"

# Check if language is set to Japanese
is_japanese = switch_language(language)

# Update title and text based on the selected language
st.title("🖋 ポニー・スマートアシスタント" if is_japanese else "🖋 Pony Smart Assistant")

# Load the data file from the directory
data_file_path = "data.txt"
try:
    with open(data_file_path, "r", encoding="utf-8") as file:
        article = file.read()
        article = truncate_text(article, 6000)  # 限制文章长度
        
except FileNotFoundError:
    st.error("データファイル 'data.txt' が見つかりません。" if is_japanese else "Data file 'data.txt' not found. Please ensure it exists.")
    st.stop()



# Question input box
question_placeholder = "参考のための質問例" if is_japanese else "Example Questions for Reference"
question = st.text_input(
    "質問入力ボックス" if is_japanese else "Question Input Box",
    placeholder=question_placeholder,
)
question = truncate_text(question, 500)  # 限制问题长度

if question and not openai_api_key:
    st.info("OpenAI APIキーを追加してください。" if is_japanese else "Please add your API key to continue.")

if question and openai_api_key:
    prompt = f"""Here's an article:\n\n<article>\n{article}\n\n</article>\n\n{question}"""
    
    # Set OpenAI API key
    openai.api_key = openai_api_key

    # 组装 messages
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Here's an article:\n\n{article}\n\n{question}"},
    ]

    while count_tokens(messages) > MAX_TOKENS:
        article = truncate_text(article, len(article) - 500)  # 逐步减少 article 长度
        messages[1]["content"] = f"Here's an article:\n\n{article}\n\n{question}"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",  # You can use "gpt-3.5-turbo" or other models
            messages=messages,
            max_tokens=1000,
        )
        st.write("### Answer")
        st.write(response['choices'][0]['message']['content'])
    except openai.error.OpenAIError as e:
        st.error(f"An error occurred: {e}")

# Retry logic
def get_response_with_retry(client, retries=5, delay=2):
    for i in range(retries):
        try:
            response = client.completions.create(
                model="gpt-4-turbo",
                prompt="Your prompt here",
                max_tokens=1000
            )
            return response
        except openai.OpenAIError as e:
            print(f"Attempt {i+1} failed: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
    raise Exception("All retries failed.")
