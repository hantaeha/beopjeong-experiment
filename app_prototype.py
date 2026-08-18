import streamlit as st
import requests

st.set_page_config(page_title="대화 A", page_icon="💬", layout="centered")

# Streamlit Secrets에서 프로토타입 전용 API Key 로드
DIFY_API_KEY = st.secrets["DIFY_API_KEY_PROTOTYPE"]
DIFY_API_URL = "https://api.dify.ai/v1/chat-messages"
MAX_TURNS = 5  # 5턴 제한

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role":"assistant",
            "content":"""산골 오두막에 찾아오신 나그네여, 물 끓는 소리에 귀를 기울이며 차 한 잔 나누시지요.\n\n
            마음속에 무겁게 내려앉은 고민이나 비워내고 싶은 짐이 있다면 편히 꺼내어 놓으십시오.\n\n
            지금 그대의 발길을 붙잡고 있는 것은 무엇인지 가만히 들여다보시지요."""
        }
    ]
if "turn_count" not in st.session_state:
    st.session_state.turn_count = 0
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = ""

st.title("💬 대화 A ")
st.caption("본 대화는 총 5회의 질의응답으로 진행됩니다.")

# 지난 대화 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5턴 대화 제어
if st.session_state.turn_count >= MAX_TURNS:
    st.success("🎉 총 5회의 대화가 완료되었습니다.")
    st.info("아래 버튼을 눌러 사후 설문조사를 완료해 주세요.")
    # 그룹 A 전용 설문지 링크 (필요 시 구분값 추가)
    st.link_button("👉 그룹 A 사후 설문조사 작성하기", "https://forms.google.com/YOUR_FORM_URL_GROUP_A")

else:
    remaining_turns = MAX_TURNS - st.session_state.turn_count
    user_input = st.chat_input(f"메시지를 입력하세요 (남은 대화: {remaining_turns}회)")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        headers = {
            "Authorization": f"Bearer {DIFY_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": {},
            "query": user_input,
            "response_mode": "blocking",
            "user": "exp_user_prototype",
            "conversation_id": st.session_state.conversation_id
        }

        with st.chat_message("assistant"):
            with st.spinner("AI가 답변을 작성 중입니다..."):
                try:
                    res = requests.post(DIFY_API_URL, headers=headers, json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        answer = data.get("answer", "")
                        st.session_state.conversation_id = data.get("conversation_id", "")
                        
                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                        st.session_state.turn_count += 1
                        st.rerun()
                    else:
                        st.error("응답 처리 중 오류가 발생했습니다.")
                except Exception as e:
                    st.error(f"연결 오류: {e}")
