import pandas as pd
import pykakasi
import requests, json
import ast, csv, re, io
from PIL import Image, ImageDraw, ImageFont
import os
from dotenv import load_dotenv
load_dotenv()

LLM_HOST = os.getenv("LLM_HOST")
EMAIL_VERIFY_API_KEY = os.getenv("EMAIL_VERIFY_API_KEY")

kakasi = pykakasi.kakasi()
def convert_to_romaji(text):
    if pd.isna(text):  # Kiểm tra nếu giá trị là NaN (Not a Number)
        return ""
    # Tách các tên theo dấu xuống dòng, chuyển đổi từng tên và ghép lại bằng dấu xuống dòng
    lines = text.split('\n')
    romaji_lines = []
    for line in lines:
        result = kakasi.convert(line)
        romaji = " ".join(item['hepburn'] for item in result)
        romaji_lines.append(romaji)
    return "\n".join(romaji_lines)

def convert_columns_to_romaji(df, columns):
    
    for column in columns:
        df[f"{column} Romaji"] = df[column].apply(convert_to_romaji)
    return df

def extract_email_array(text):
    # Regular expression pattern to find the array within the text
    pattern = r"\[.*\]"
    
    # Find the array in the text
    match = re.search(pattern, text)
    
    if match:
        array_str = match.group()
        # Convert the string representation of the array to an actual list
        email_array = ast.literal_eval(array_str)
        return email_array
    else:
        return []

def get_email_from_romaji(domain, name):
    url = f"https://f881-14-232-214-101.ngrok-free.app/v1/chat/completions"
    payload = json.dumps({
    "model": "bartowski/Phi-3.1-mini-4k-instruct-GGUF",
    "messages": [
        {
        "role": "system",
        "content": "Your answer always return in array format."
        },
        {
        "role": "user",
        "content":f"""
            Generate at least 10 email addresses based on a person's name: {name} and the company's domain: {domain}.
            Use common email patterns and return the result in an array format.
            Only include the array of emails, nothing else.

            Example:
            Name: David Chung
            Domain: code2trade.top

            Output:
            ["david.chung@code2trade.top", "d.chung@code2trade.top", "david@code2trade.top", "chung.david@code2trade.top", "dchung@code2trade.top", "david_c@code2trade.top", "davidc@code2trade.top", "david.ch@code2trade.top", "chung@code2trade.top", "dch@code2trade.top", "davidchung@code2trade.top", "chungdavid@code2trade.top", "david-chung@code2trade.top", "chung-david@code2trade.top"]
        """
        }
    ],
    "temperature": 0.9,
    "max_tokens": -1,
    "stream": False
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    data = response.json()
    return extract_email_array(data['choices'][0]['message']['content'])

from emailverify import  EmailListVerifyBulk
import os


def verify_email(emails):
    # Đường dẫn lưu file CSV
    # os.makedirs('/temp_email_list', exist_ok=True)
    csv_file_path = 'non_verify_emails.csv'
    
    # Lưu các email vào file CSV
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Email'])  # Ghi tiêu đề cột
        for email in emails:
            writer.writerow([email])
    
    # Gửi file CSV này đến một API khác
    B = EmailListVerifyBulk('d1PX3kpDLRIFFk39GjuNX', csv_file_path)
    B.upload()
    verified_email_list_url = B.get_info()
    return download_and_extract_emails(verified_email_list_url)

def download_and_extract_emails(url):
    response = requests.get(url)
    response.raise_for_status()  # Ensure we notice bad responses
    emails = []

    with open('verified_emails.csv', 'w') as file:
        file.write(response.text)
    
    with open('verified_emails.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            emails.append(row['Email'])
    
    return emails


def generate_business_card(template_path, name, job_title, phone_number, company_address, email_address):
    # Open the business card template
    template = Image.open(template_path)
    draw = ImageDraw.Draw(template)
    
    # Define font and text positions
    # font = ImageFont.load_default(size=15)
    font_path = "NotoSansJP-VariableFont_wght.ttf"  # Đường dẫn đến file font Noto Sans JP
    font = ImageFont.truetype(font_path, size=15)
    
    # Define positions for each text element
    name_position = (50, 50)
    job_title_position = (50, 74)
    phone_number_position = (50, 112)
    email_address_position = (50, 130)
    company_address_position = (50, 165)
    
    
    # Add text to the template
    draw.text(name_position, f"{name}", font=font, fill="black")
    draw.text(job_title_position, f"{job_title}", font=font, fill="black")
    draw.text(phone_number_position, f"Phone: {phone_number}", font=font, fill="black")
    draw.text(company_address_position, f"Address: {company_address}", font=font, fill="black")
    draw.text(email_address_position, f"Email: {email_address}", font=font, fill="black")
    
    # Save the edited business card
    img_byte_arr = io.BytesIO()
    template.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    return img_byte_arr