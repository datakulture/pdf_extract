import streamlit as st
import pdf2image
import pytesseract
from pytesseract import Output, TesseractError
import base64
from io import StringIO

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

from streamlit_js_eval import get_geolocation

import yaml

from yaml.loader import SafeLoader


import streamlit_authenticator as stauth

st.set_page_config(page_title="PDF to Text")

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'] 
)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    authenticator.logout('Logout', 'main')
    st.write(f'Welcome *{name}*')
    
    #st.title('Some content')
elif authentication_status is False:
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username and password')
#from functions import convert_pdf_to_txt_pages, convert_pdf_to_txt_file, save_pages, displayPDF, images_to_txt

def displayPDF(file):
  # Opening file from file path
  # with open(file, "rb") as f:
  base64_pdf = base64.b64encode(file).decode('utf-8')

  # Embedding PDF in HTML
  #pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
  pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">' 

  # Displaying File
  st.markdown(pdf_display, unsafe_allow_html=True)

@st.cache
def convert_pdf_to_txt_file(path):
    texts = []
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    # fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    
    file_pages = PDFPage.get_pages(path)
    nbPages = len(list(file_pages))
    for page in PDFPage.get_pages(path):
      interpreter.process_page(page)
      t = retstr.getvalue()
    # text = retstr.getvalue()

    # fp.close()
    device.close()
    retstr.close()
    return t, nbPages


@st.cache
def images_to_txt(path, language):
    images = pdf2image.convert_from_bytes(path)
    all_text = []
    for i in images:
        pil_im = i
        text = pytesseract.image_to_string(pil_im, lang=language)
        # ocr_dict = pytesseract.image_to_data(pil_im, lang='eng', output_type=Output.DICT)
        # ocr_dict now holds all the OCR info including text and location on the image
        # text = " ".join(ocr_dict['text'])
        # text = re.sub('[ ]{2,}', '\n', text)
        all_text.append(text)
    return all_text, len(all_text)


if authentication_status:

    html_temp = """
                <div style="background-color:{};padding:1px">
                
                </div>
                """

    # st.markdown("""
    #     ## :outbox_tray: Text data extractor: PDF to Text
        
    # """)
    # st.markdown(html_temp.format("rgba(55, 53, 47, 0.16)"),unsafe_allow_html=True)
    st.markdown("""
        ## Text data extractor: PDF to Text
        
    """)
    languages = {
        'English': 'eng',
        'French': 'fra',
        'Arabic': 'ara',
        'Spanish': 'spa',
    }

    with st.sidebar:
        st.title(":outbox_tray: PDF to Text")
        
        ocr_box = st.checkbox('Enable OCR (scanned document)')
        
        st.markdown(html_temp.format("rgba(55, 53, 47, 0.16)"),unsafe_allow_html=True)
        st.markdown("""
        # How does it work?
        Simply load your PDF and convert it to single-page or multi-page text.
        """)
        st.markdown(html_temp.format("rgba(55, 53, 47, 0.16)"),unsafe_allow_html=True)
        
        

    pdf_file = st.file_uploader("Load your PDF", type="pdf")
    hide="""
    <style>
    footer{
        visibility: hidden;
            position: relative;
    }
    .viewerBadge_container__1QSob{
        visibility: hidden;
    }
    #MainMenu{
        visibility: hidden;
    }
    <style>
    """
    st.markdown(hide, unsafe_allow_html=True)
    if pdf_file:
        path = pdf_file.read()
        # display document
        with st.expander("Display document"):
            displayPDF(path)
        if ocr_box:
            option = st.selectbox('Select the document language', list(languages.keys()))
        # pdf to text
    
        if ocr_box:
            texts, nbPages = images_to_txt(path, languages[option])
            totalPages = "Pages: "+str(nbPages)+" in total"
            text_data_f = "\n\n".join(texts)
        else:
            text_data_f, nbPages = convert_pdf_to_txt_file(pdf_file)
            totalPages = "Pages: "+str(nbPages)+" in total"

        st.info(totalPages)
        st.download_button("Download txt file", text_data_f)

    if st.checkbox("Check my location"):
        loc = get_geolocation()
        st.write(f"Your coordinates are {loc}")

    
    
