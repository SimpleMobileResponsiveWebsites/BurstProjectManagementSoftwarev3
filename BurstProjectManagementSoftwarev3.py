import streamlit as st
from io import BytesIO
import base64
from streamlit_ace import st_ace
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# Initialization of session state variables with new keys for packages, Node version, and NPM version
session_state_keys = [
    'task_list', 'framework_dict', 'language_dict', 'modules_dict',
    'text_dict', 'code_dict', 'css_dict', 'html_dict', 'packages_dict',
    'node_version_dict', 'npm_version_dict'
]
for key in session_state_keys:
    if key not in st.session_state:
        st.session_state[key] = [] if key == 'task_list' else {}

def create_download_link_pdf(pdf_data, download_filename):
    b64 = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{download_filename}">Download PDF</a>'
    return href

def gather_user_inputs():
    app_version = st.text_input("App Version:")
    if st.button("Save App Version") and app_version:
        if app_version not in st.session_state.task_list:
            st.session_state.task_list.append(app_version)

    detail_keys = [
        "Framework", "Languages", "Modules", "Regression Testing Notes",
        "Packages", "Node Version", "NPM Version"
    ]
    detail_dicts = [
        "framework_dict", "language_dict", "modules_dict", "text_dict",
        "packages_dict", "node_version_dict", "npm_version_dict"
    ]

    for detail, dict_key in zip(detail_keys, detail_dicts):
        input_type = st.text_area if detail in ["Regression Testing Notes", "Packages"] else st.text_input
        user_input = input_type(f"{detail} being used:")
        save_button = st.button(f"Save {detail}")

        if save_button and user_input:
            st.session_state[dict_key].setdefault(app_version, []).append(
                user_input.split(',') if ',' in user_input else user_input)

    # Adjusted code input areas
    st.caption("Enter your Javascript code here:")
    js_code_input = st_ace(language="javascript", theme="monokai", key=f"js_code_{app_version}")
    if st.button("Save Javascript Code") and js_code_input:
        st.session_state['code_dict'].setdefault(app_version, []).append(js_code_input)

    st.caption("Enter your CSS code here:")
    css_code_input = st_ace(language="css", theme="monokai", key=f"css_code_{app_version}")
    if st.button("Save CSS Code") and css_code_input:
        st.session_state['css_dict'].setdefault(app_version, []).append(css_code_input)

    st.caption("Enter your HTML code here:")
    html_code_input = st_ace(language="html", theme="monokai", key=f"html_code_{app_version}")
    if st.button("Save HTML Code") and html_code_input:
        st.session_state['html_dict'].setdefault(app_version, []).append(html_code_input)

def display_saved_items():
    st.write("## Saved Items")
    for version in st.session_state.task_list:
        st.write(f"### App Version: {version}")
        for key in [
            'framework_dict', 'language_dict', 'modules_dict', 'text_dict',
            'code_dict', 'css_dict', 'html_dict', 'packages_dict',
            'node_version_dict', 'npm_version_dict'
        ]:
            label = key.replace('_dict', '').capitalize()
            items = st.session_state[key].get(version, [])
            if items:
                st.write(f"#### {label}:")
                for item in items:
                    display_content = ', '.join(item) if isinstance(item, list) and key not in ['code_dict', 'css_dict', 'html_dict'] else item
                    if key in ['code_dict', 'css_dict', 'html_dict']:
                        language = 'javascript' if key == 'code_dict' else key.replace('_dict', '')
                        st.code(display_content, language=language)
                    else:
                        st.write(f"- {display_content}")

def generate_pdf_content():
    styles = getSampleStyleSheet()
    elements = []
    for version in st.session_state.task_list:
        elements.append(Paragraph(f"App Version: {version}", styles['Heading2']))
        elements.append(Spacer(1, 0.2 * inch))
        for key in [
            'framework_dict', 'language_dict', 'modules_dict', 'text_dict',
            'code_dict', 'css_dict', 'html_dict', 'packages_dict',
            'node_version_dict', 'npm_version_dict'
        ]:
            label = key.replace('_dict', '').capitalize()
            items = st.session_state[key].get(version, [])
            if items:
                elements.append(Paragraph(f"{label}:", styles['Heading3']))
                for item in items:
                    content = ', '.join(item) if isinstance(item, list) else item
                    content = content.replace('<', '&lt;').replace('>', '&gt;')
                    style = styles['Code'] if key in ['code_dict', 'css_dict', 'html_dict'] else styles['BodyText']
                    elements.append(Paragraph(content, style))
                elements.append(Spacer(1, 0.2 * inch))
        elements.append(PageBreak())
    return elements

gather_user_inputs()
display_saved_items()

if st.button("Generate PDF"):
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, leftMargin=50, rightMargin=50, topMargin=50, bottomMargin=50)
    elements = generate_pdf_content()
    doc.build(elements)
    pdf_buffer.seek(0)
    pdf_data = pdf_buffer.getvalue()
    st.markdown(create_download_link_pdf(pdf_data, "App_Details.pdf"), unsafe_allow_html=True)
