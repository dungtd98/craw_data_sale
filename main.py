import streamlit as st
import pandas as pd
from utils import convert_columns_to_romaji, get_email_from_romaji, verify_email, generate_business_card
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode

def upload_file():
    st.header("Upload Excel File")
    uploaded_file = st.file_uploader("Chọn file Excel", type=["xlsx"])
    if uploaded_file:
        sheets = pd.ExcelFile(uploaded_file).sheet_names
        sheet = st.selectbox("Chọn sheet", sheets)
        df = pd.read_excel(uploaded_file, sheet_name=sheet, header=3)
        
        # Convert all column names to strings
        df.columns = df.columns.astype(str)
        
        st.dataframe(df)
        
        columns = st.multiselect("Chọn các cột để hiển thị", df.columns)
        name_columns = st.multiselect("Chọn cột tên người đại diện", columns)
        domain_column = st.selectbox("Chọn cột domain công ty", columns)
        job_title_column = st.selectbox("Chọn cột chức vụ", columns)
        company_address_column = st.selectbox("Chọn cột địa chỉ công ty", columns)
        company_phone_column = st.selectbox("Chọn cột số điện thoại công ty", columns)
        
        if st.button("Confirm"):
            save_session_state(df, columns, name_columns, domain_column, job_title_column, company_address_column, company_phone_column, uploaded_file, sheet)
            st.success("Đã xác nhận các cột đã chọn. Chuyển sang trang Confirm Selection.")

def save_session_state(df, columns, name_columns, domain_column, job_title_column, company_address_column, company_phone_column, uploaded_file, sheet):
    st.session_state['df'] = df
    st.session_state['columns'] = columns
    st.session_state['name_columns'] = name_columns
    st.session_state['domain_column'] = domain_column
    st.session_state['job_title_column'] = job_title_column
    st.session_state['company_address_column'] = company_address_column
    st.session_state['company_phone_column'] = company_phone_column
    st.session_state['uploaded_file'] = uploaded_file
    st.session_state['sheet'] = sheet
    st.session_state['emails_df'] = None
    st.session_state['selected_emails'] = None

def confirm_selection():
    st.header("Confirm Column Selection")
    if validate_session_state():
        df, columns, name_columns, domain_column, job_title_column, company_address_column, company_phone_column = load_session_state()
        rename_dict, name_columns_romaji = get_rename_dict_and_romaji_columns(name_columns, domain_column, job_title_column, company_address_column, company_phone_column)
        df = df.rename(columns=rename_dict)
        st.write(f"File: {st.session_state['uploaded_file'].name}")
        st.write(f"Sheet: {st.session_state['sheet']}")
        df = convert_columns_to_romaji(df, name_columns)
        display_columns = get_display_columns(columns, name_columns, ['company domain', 'job title', 'company address', 'company phone'])
        display_columns = filter_existing_columns(df, display_columns)
        display_data_table(df, display_columns)
        handle_generate_email(df, name_columns, display_columns)

def validate_session_state():
    required_keys = ['df', 'columns', 'name_columns', 'domain_column', 'job_title_column', 'company_address_column', 'company_phone_column']
    return all(key in st.session_state for key in required_keys)

def load_session_state():
    return (
        st.session_state['df'],
        st.session_state['columns'],
        st.session_state['name_columns'],
        st.session_state['domain_column'],
        st.session_state['job_title_column'],
        st.session_state['company_address_column'],
        st.session_state['company_phone_column']
    )

def get_rename_dict_and_romaji_columns(name_columns, domain_column, job_title_column, company_address_column, company_phone_column):
    rename_dict = {
        domain_column: 'company domain',
        job_title_column: 'job title',
        company_address_column: 'company address',
        company_phone_column: 'company phone'
    }
    name_columns_romaji = [f"{col} Romaji" for col in name_columns]
    return rename_dict, name_columns_romaji

def get_display_columns(columns, name_columns, additional_columns):
    display_columns = []
    for col in name_columns:
        display_columns.append(col)
        display_columns.append(f"{col} Romaji")
    display_columns += additional_columns
    return display_columns

def filter_existing_columns(df, columns):
    return [col for col in columns if col in df.columns]

def display_data_table(df, display_columns):
    df_display = df[display_columns].copy()
    gb = GridOptionsBuilder.from_dataframe(df_display)
    gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren=True)
    grid_options = gb.build()
    grid_response = AgGrid(
        df_display,
        gridOptions=grid_options,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        fit_columns_on_grid_load=True,
        enable_enterprise_modules=True,
        height=400,
        width='100%',
        reload_data=True,
        key="selected_data_table"
    )
    st.session_state['selected_rows'] = pd.DataFrame(grid_response['selected_rows'])

def handle_generate_email(df, name_columns, display_columns):
    if st.button("Generate email"):
        selected_rows = st.session_state['selected_rows']
        
        if selected_rows.empty:
            st.warning("Vui lòng chọn ít nhất một hàng để gửi API.")
        else:
            romaji_columns_selected = [f"{col} Romaji" for col in name_columns]
            if not set(romaji_columns_selected).issubset(selected_rows.columns):
                st.error("Error: Not all selected columns are in the DataFrame")
            else:
                emails_df = generate_emails(selected_rows, romaji_columns_selected)
                if not emails_df.empty:
                    st.session_state['emails_df'] = emails_df
                    display_generated_emails(emails_df)
                else:
                    st.warning("Không có email nào hợp lệ.")

def generate_emails(selected_rows, romaji_columns_selected):
    emails_list = []
    for idx, row in selected_rows.iterrows():
        romaji_data = row[romaji_columns_selected].to_dict()
        company_domain = row['company domain']
        emails = get_email_from_romaji(company_domain, romaji_data)
        # verified_email = verify_email(emails)
        for email in emails:
            new_row = row.copy()
            new_row['Verified Email'] = email
            emails_list.append(new_row)
    return pd.DataFrame(emails_list) if emails_list else pd.DataFrame()

# def display_generated_emails(emails_df):
#     if 'selected_emails' not in st.session_state:
#         st.session_state['selected_emails'] = pd.DataFrame()

#     gb = GridOptionsBuilder.from_dataframe(emails_df)
#     gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren=True)
#     grid_options = gb.build()
    
#     grid_response = AgGrid(
#         emails_df,
#         gridOptions=grid_options,
#         data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
#         update_mode=GridUpdateMode.SELECTION_CHANGED,
#         fit_columns_on_grid_load=True,
#         enable_enterprise_modules=True,
#         height=400,
#         width='100%',
#         reload_data=False,
#         key="generated_emails_table"
#     )
    
#     selected_emails = pd.DataFrame(grid_response['selected_rows'])
#     st.session_state['selected_emails'] = selected_emails

#     if st.button("Generate business card"):
#         generate_business_cards(st.session_state['selected_emails'])

def display_generated_emails(emails_df):
    if 'selected_emails' not in st.session_state:
        st.session_state['selected_emails'] = pd.DataFrame()
    st.table(emails_df)
    for idx, row in emails_df.iterrows():
        name = row.get('Contact point', '')
        job_title = row.get('job title', '')
        phone_number = row.get('company phone', '')
        company_address = row.get('company address', '')
        email_address = row.get('Verified Email', '')
        card_image = generate_business_card(
                template_path='./assets/Namecard.png',
                name=name,
                job_title=job_title,
                phone_number=phone_number,
                company_address=company_address,
                email_address=email_address
            )
        st.image(card_image, caption=f"Business Card for {name}", use_column_width=True)
    
def generate_business_cards(selected_emails):
    if selected_emails.empty:
        st.warning("Vui lòng chọn ít nhất một hàng để tạo danh thiếp.")
    else:
        for idx, row in selected_emails.iterrows():
            name = f"{row['name']}"
            job_title = row['job title']
            phone_number = row['company phone']
            company_address = row['company address']
            email_address = row['Verified Email']
            card_image = generate_business_card(
                template_path='./assets/Namecard.png',
                name=name,
                job_title=job_title,
                phone_number=phone_number,
                company_address=company_address,
                email_address=email_address
            )
            st.image(card_image, caption=f"Business Card for {name} and email: {email_address}", use_column_width=True)

st.title("Excel Column Selector and Converter")

page = st.sidebar.selectbox("Chọn trang", ["Upload File", "Confirm Selection"])

if page == "Upload File":
    upload_file()
elif page == "Confirm Selection":
    confirm_selection()
