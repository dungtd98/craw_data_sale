from PIL import Image, ImageDraw, ImageFont

def edit_business_card(template_path, output_path, name, job_title, phone_number, company_address, email_address):
    # Open the business card template
    template = Image.open(template_path)
    draw = ImageDraw.Draw(template)
    
    # Define font and text positions
    font_path = "NotoSansJP-VariableFont_wght.ttf"  # Đường dẫn đến file font Noto Sans JP
    font = ImageFont.truetype(font_path, size=15)
    
    
    # Define positions for each text element
    name_position = (50, 50)
    job_title_position = (50, 75)
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
    template.save(output_path)

# Example usage
edit_business_card(
    template_path="./assets/Namecard.png",
    output_path="./assets/edited_business_card.png",
    name="伊藤康浩",
    job_title="代表取締役",
    phone_number="080-5089-4523",
    company_address="東京都千代田区神田平河町１番地",
    email_address="ito.y@saze.co.jp"
)
