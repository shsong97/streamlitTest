import streamlit as st
import hashlib
import os
import json
from typing import Tuple, Optional

# /pages/loginauth.py
# Streamlit 기반 간단 로그인/회원가입 인증 예제
# 파일 기반 사용자 저장 (users.json) + PBKDF2 해시


st.set_page_config(page_title="Login Auth", page_icon="🔒", layout="centered")

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")
PBKDF2_ITERATIONS = 100_000

def load_users() -> dict:
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_users(users: dict):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def hash_password(password: str, salt: Optional[bytes] = None) -> Tuple[str, str]:
    if salt is None:
        salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return salt.hex(), dk.hex()

def verify_password(stored_salt_hex: str, stored_hash_hex: str, password_attempt: str) -> bool:
    salt = bytes.fromhex(stored_salt_hex)
    _, attempt_hash = hash_password(password_attempt, salt)
    return attempt_hash == stored_hash_hex

# 세션 초기화
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

users = load_users()

st.title("로그인 인증 (Streamlit)")

# 좌측 사이드바: 로그인 또는 로그아웃
with st.sidebar:
    if st.session_state.logged_in:
        st.write(f"로그인: {st.session_state.user}")
        if st.button("로그아웃"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()
    else:
        st.write("계정이 없으면 아래에서 회원가입하세요.")

# 메인: 로그인 폼
if not st.session_state.logged_in:
    with st.form("login_form"):
        st.subheader("로그인")
        username = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        remember = st.checkbox("로그인 상태 유지 (세션 기반)")
        submitted = st.form_submit_button("로그인")
        if submitted:
            if not username or not password:
                st.error("아이디와 비밀번호를 입력하세요.")
            elif username not in users:
                st.error("존재하지 않는 사용자입니다.")
            else:
                info = users[username]
                if verify_password(info["salt"], info["hash"], password):
                    st.session_state.logged_in = True
                    st.session_state.user = username
                    st.success("로그인 성공")
                    if remember:
                        # 간단 구현: 세션에 남겨둠 (Streamlit은 세션 단위 유지)
                        pass
                    st.rerun()
                else:
                    st.error("비밀번호가 일치하지 않습니다.")

    st.markdown("---")
    # 회원가입
    with st.expander("회원가입"):
        with st.form("register_form"):
            st.subheader("새 계정 생성")
            new_username = st.text_input("아이디 (영문/숫자 추천)", key="reg_user")
            new_password = st.text_input("비밀번호 (6자 이상)", type="password", key="reg_pass")
            new_password2 = st.text_input("비밀번호 확인", type="password", key="reg_pass2")
            register = st.form_submit_button("회원가입")
            if register:
                if not new_username or not new_password:
                    st.error("아이디와 비밀번호를 입력하세요.")
                elif len(new_password) < 6:
                    st.error("비밀번호는 6자 이상이어야 합니다.")
                elif new_password != new_password2:
                    st.error("비밀번호가 일치하지 않습니다.")
                elif new_username in users:
                    st.error("이미 존재하는 아이디입니다.")
                else:
                    salt_hex, hash_hex = hash_password(new_password)
                    users[new_username] = {"salt": salt_hex, "hash": hash_hex}
                    save_users(users)
                    st.success("회원가입 완료. 로그인해주세요.")
else:
    # 인증된 사용자에게만 보여줄 내용
    st.success(f"환영합니다, {st.session_state.user}님 ✅")
    st.write("여기에 인증된 사용자만 볼 수 있는 내용을 넣으세요.")
    # 예: 간단한 사용자 정보 보기
    if st.button("내 정보 보기"):
        info = users.get(st.session_state.user, {})
        st.json({"username": st.session_state.user, "salt": info.get("salt"), "hash": info.get("hash")})