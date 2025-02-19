import streamlit as st

pg = st.navigation([st.Page(page="000_Learn_French.py", url_path='Learn_French'),
                    st.Page(page="00_English_to_french.py", url_path='English_to_french'),
                    st.Page(page="01_French_to_english.py", url_path='French_to_english')])
pg.run()
