import streamlit as st
import base64

@st.cache_data
def get_base64_of_img(image):
    with open(image, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def style_sidebar_area(sidebar_img_path):
    side_img_data = get_base64_of_img(sidebar_img_path)
    sidebar_bg_img = f"""
    <style>
    [data-testid="stSidebar"] {{
    background-image: url("data:image/png;base64,{side_img_data}");
    }}

    [data-testid="stSidebarUserContent"] {{
    background-color: rgba(0, 0, 0, 0);
    }}
    
    [data-testid="stButton"] {{
    background-color: black;
    opacity: 0.5;
    transition: 0.5s
    border-radius: 20px;
    }}
    
    [data-testid="stButton"]:hover {{
    opacity: 1;
    }}
    </style>
"""
    st.markdown(sidebar_bg_img, unsafe_allow_html=True)


def style_chat_area(chat_img_path):
    chat_img_data = get_base64_of_img(chat_img_path)
    page_bg_image=f"""
    <style>
    [data-testid="stApp"] {{
        background-image: url("data:image/png;base64,{chat_img_data}");
        background-size: stretch;
    }}

    [data-testid="stHeader"] {{
        background-color: rgba(0, 0, 0, 0);
    }}

    [data-testid="stToolbar"] {{
        color: rgba(0, 0, 0, 0);
    }}
    
    [data-testid="stChatMessage"] {{
    background-color: black;
    }}
    
    [data-testid="stHeader"] {{
    height:0px;
    }}
    
    [data-testid="stAlert"] {{
    background-color: black;
    border-radius: 0.5;
    }}
    
    [data-testid="stNotification"] {{
    background-color: black;
    }}

    [data-testid="stNotificationContentInfo"] {{
        color: white;
        font-weight: bold;
        opacity: 1;
    }}
    
    [data-testid="stExpander"] {{
        color: Black;
        font-weight: bold;
        opacity: 0.5;
        transition: 0.5s;
        border-radius: 10px;
    }}
    
    [data-testid="stExpander"]:hover {{
        background-color: black;
        opacity: 1;
    }}
    
    [data-testid="stHorizontalBlock"] {{
        opacity: 0.3;
        transition: 0.5s;
        border-radius: 15px;
    }}
    
    [data-testid="stHorizontalBlock"]:hover {{
        opacity: 1;
        border-style: solid;
        border-width: 2px;
        border-color: red;
        background-color: black;
    }}
    
    [data-testid="stBottom"] {{
        opacity:0.5;
        border-radius:100px;
    }}
    
    [data-testid="stBottom"]:hover {{
        opacity:1;
    }}
    
    [data-testid="stChatInput"] {{
        opacity:0.5;
    }}
    [data-testid="stChatInput"]:hover {{
        border-style:solid;
        border-color: red;
        opacity:1;
    }}
    </style>
    """
    st.markdown(page_bg_image, unsafe_allow_html=True)

def img_to_html(img_path):
    img_html = "<div style='display: flex; justify-content: center; align-items: center; height: 20vh; border: 1px solid white; background-color: white; margin-bottom: 10px; border-radius: 50%'><img src='data:image/png;base64,{}'alt='Centered Image' style='max-width: 80%; max-height: 80%;'></div>".format(get_base64_of_img(img_path))
    return img_html