from openai import OpenAI
import streamlit as st
import pandas as pd

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("AIよしむら（統計学）")

# data
df = pd.read_csv('data/combined1.csv')
#data1 = df["説明"]
data1 = df["説明"][0:10]
data2 = data1.to_string()
#st.markdown(df.head())

# template
template = '''
あなたは経済学部の2年次開講科目「統計学A」を担当する大学教員です。
35歳、教員歴は8年目の准教授です。専門は計量経済学で、ゼミも計量経済学です。
この講義に関する学生からの質問に答えてください。

### 条件
- 教授らしく厳格な言葉遣いで、ただし質問者に分かり易く、簡潔に答えてください。
- 全ての質問に対して、講義内容に関する以下の詳細な「事前資料」を参照した上で、正確に答えてください。
- とりわけ成績評価に関する内容については、事前資料を正確に参照した上で答えてください（小テスト・中間テスト・最終テストについて）。
- 小テストは12回分あります。合計で70%の配分です。中間テストは15％の配分、最終テストは15%分の配分です。
- 事前資料に無い内容を質問された場合、GPTで答えられる一般的な内容を答えてください。数値例などを用いた解答もしてください。

### 事前資料
"""__MSG__"""
'''

template2 = template.replace('__MSG__', data2.replace('"', ''))

# OpenAIのモデルを指定
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# チャットの履歴 messages を初期化（一つ一つの messages は {role, content} の形式）
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages = [{'role': 'system', 'content': template2}]
    

# それまでのメッセージを全て表示したままにする（このloopがないと、同じ場所を更新しながら会話が続く）
for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"]) # 表示する（一瞬ですべて書き下す）


# 入力されたら、内容をpromptに格納(入力までは待機)
if prompt := st.chat_input("質問はありますか？"):
    # messagesにユーザーのプロンプトを追加
    st.session_state.messages.append({"role": "user", "content": prompt})

    # ユーザーのアイコンで、promptをそのまま表示
    with st.chat_message("user"):
        st.markdown(prompt)

    # AIのアイコンで
    with st.chat_message("assistant"):
        # ChatGPTの返答をstreamに格納
        stream = client.chat.completions.create(
            model = st.session_state["openai_model"],
            # 会話履歴をすべて参照して渡す
            messages = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream = True,
            temperature = 0.5,
        )
        # AIの返答を流れるように出力
        response = st.write_stream(stream)
    
    # messagesにAIの返答を格納
    st.session_state.messages.append({"role": "assistant", "content": response})
    #　ここで一旦終わり、入力待機となる
