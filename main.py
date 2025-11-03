import streamlit as st
st.title('나의 첫 웹 서비스 만들기!')
name=st.text_imput('이름을 입력하세요:')
if st.botton('인사말 생성'):
  st.wirte(name+'님! 안녕하세요')
