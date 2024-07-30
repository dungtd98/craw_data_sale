import pandas as pd
import pykakasi
import requests, json
import re
import ast

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
    url = "http://localhost:1234/v1/chat/completions"
    payload = json.dumps({
    "model": "TheBloke/Mistral-7B-Instruct-v0.2-GGUF",
    "messages": [
        {
        "role": "system",
        "content": "Your answer always return in array format."
        },
        {
        "role": "user",
        "content":f"""
            This is company domain: {domain}
            This is provided name: {name}
            Base on provided company domain and name, please give me at least 10 email address.
            Your answer always return in array format.
            The answer must be in pattern: "[email1,email2,...]"
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