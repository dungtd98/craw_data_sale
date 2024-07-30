
import streamlit as st
import pandas as pd
from utils import convert_columns_to_romaji, get_email_from_romaji
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode

st.title("Excel Column Selector and Converter")

# Sử dụng st.sidebar để tạo các trang
page = st.sidebar.selectbox("Chọn trang", ["Upload File", "Confirm Selection"])

# Trang upload file
if page == "Upload File":
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
        romaji_columns = st.multiselect("Chọn các cột để chuyển sang Romaji", columns)
        domain_column = st.selectbox("Chọn cột là domain của công ty", df.columns)
        
        if st.button("Confirm"):
            st.session_state['df'] = df
            st.session_state['columns'] = columns
            st.session_state['romaji_columns'] = romaji_columns
            st.session_state['domain_column'] = domain_column
            st.session_state['uploaded_file'] = uploaded_file
            st.session_state['sheet'] = sheet
            st.session_state['emails_df'] = None
            st.session_state['selected_emails'] = None
            st.success("Đã xác nhận các cột đã chọn. Chuyển sang trang Confirm Selection.")

# Trang xác nhận lựa chọn
if page == "Confirm Selection":
    st.header("Confirm Column Selection")
    if 'df' in st.session_state and 'columns' in st.session_state:
        df = st.session_state['df']
        columns = st.session_state['columns']
        romaji_columns = st.session_state['romaji_columns']
        domain_column = st.session_state['domain_column']
        uploaded_file = st.session_state['uploaded_file']
        sheet = st.session_state['sheet']
        
        # Đổi tên cột domain thành "company domain"
        df = df.rename(columns={domain_column: 'company domain'})
        
        st.write(f"File: {uploaded_file.name}")
        st.write(f"Sheet: {sheet}")
        
        # Chuyển đổi các cột được chọn sang Romaji
        df = convert_columns_to_romaji(df, romaji_columns)
        
        # Hiển thị dữ liệu của các cột đã chọn và các cột đã chuyển đổi sang Romaji
        display_columns = columns + [f"{col} Romaji" for col in romaji_columns]
        
        # Thêm "company domain" vào display_columns nếu nó không có trong columns ban đầu
        if 'company domain' not in display_columns:
            display_columns.append('company domain')
        
        # Đảm bảo tất cả các cột tồn tại trong DataFrame trước khi hiển thị
        display_columns = [col for col in display_columns if col in df.columns]
        
        # Tạo checkbox cho từng hàng
        gb = GridOptionsBuilder.from_dataframe(df[display_columns])
        gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren=True)
        grid_options = gb.build()

        grid_response = AgGrid(
            df[display_columns],
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
        
        selected_rows = pd.DataFrame(grid_response['selected_rows'])
        
        if st.button("Generate email"):
            if selected_rows.empty:
                st.warning("Vui lòng chọn ít nhất một hàng để gửi API.")
            else:
                # Chỉ lấy các cột Romaji để gửi API
                romaji_columns_selected = [f"{col} Romaji" for col in romaji_columns]
                
                if not set(romaji_columns_selected).issubset(selected_rows.columns):
                    st.error("Error: Not all selected columns are in the DataFrame")
                else:
                    emails_list = []
                    for idx, row in selected_rows.iterrows():
                        romaji_data = row[romaji_columns_selected].to_dict()
                        company_domain = row['company domain']
                        emails = get_email_from_romaji(company_domain, romaji_data)
                        
                        for email in emails:
                            new_row = row.copy()
                            new_row['Possible Email'] = email
                            emails_list.append(new_row)
                    
                    emails_df = pd.DataFrame(emails_list)
                    st.session_state['emails_df'] = emails_df
        
        # Hiển thị bảng đã tạo email
        if st.session_state.get('emails_df') is not None:
            emails_df = st.session_state['emails_df']
            
            gb = GridOptionsBuilder.from_dataframe(emails_df)
            gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren=True)
            grid_options = gb.build()

            grid_response = AgGrid(
                emails_df,
                gridOptions=grid_options,
                data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
                update_mode=GridUpdateMode.SELECTION_CHANGED,
                fit_columns_on_grid_load=True,
                enable_enterprise_modules=True,
                height=400,
                width='100%',
                reload_data=True,
                key="generated_emails_table"
            )
            
            selected_emails = pd.DataFrame(grid_response['selected_rows'])
            st.session_state['selected_emails'] = selected_emails
            
            if st.button("Generate business card"):
                if selected_emails.empty:
                    st.warning("Vui lòng chọn ít nhất một hàng để tạo danh thiếp.")
                else:
                    # Hiển thị thông báo thành công cho từng hàng đã chọn
                    for idx, row in selected_emails.iterrows():
                        st.success(f"Generate success for {row['Possible Email']}, Company: {row['company domain']}, Name: {row['first_name']} {row['last_name']}")
    else:
        st.warning("Vui lòng upload file và chọn các cột trước.")