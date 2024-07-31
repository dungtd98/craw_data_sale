from PIL import Image, ImageDraw, ImageFont

def edit_business_card(template_path, output_path, name, job_title, phone_number, company_address, email_address):
    # Open the business card template
    template = Image.open(template_path)
    draw = ImageDraw.Draw(template)
    
    # Define font and text positions
    font = ImageFont.load_default(size=15)
    
    
    # Define positions for each text element
    name_position = (50, 50)
    job_title_position = (50, 64)
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
    name="John Doe",
    job_title="Software Engineer",
    phone_number="+1234567890",
    company_address="1234 Elm Street, City, Country",
    email_address="john.doe@example.com"
)
