from PIL import Image, ImageDraw, ImageFont
import os

def create_document_image(filename: str, title: str, content: list, is_faded: bool = False):
    # Dimensions for A4-style landscape/portrait card
    width, height = 900, 650
    bg_color = (245, 240, 225) if is_faded else (255, 255, 255)
    text_color = (130, 130, 130) if is_faded else (20, 20, 20)
    border_color = (180, 170, 150) if is_faded else (50, 50, 50)
    
    img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Outer formal border
    draw.rectangle([20, 20, width - 20, height - 20], outline=border_color, width=3)
    draw.rectangle([26, 26, width - 26, height - 26], outline=border_color, width=1)
    
    # Title Header Box
    draw.rectangle([30, 30, width - 30, 90], fill=(230, 235, 245) if not is_faded else (235, 230, 215))
    draw.text((45, 50), title, fill=(0, 51, 102) if not is_faded else (100, 100, 100))
    
    # Document Body Lines
    y_offset = 120
    for line in content:
        draw.text((50, y_offset), line, fill=text_color)
        y_offset += 32
        
    # Simulate stamp/seal
    seal_color = (180, 50, 50) if not is_faded else (190, 160, 160)
    draw.ellipse([width - 180, height - 160, width - 60, height - 40], outline=seal_color, width=2)
    draw.text((width - 160, height - 105), "SEAL & SIGN", fill=seal_color)
    
    img.save(filename)
    print(f"✅ Generated: {filename}")

# Generate Sample 1: Marathi 7/12
create_document_image(
    "sample_marathi_7_12.png",
    "MAHARASHTRA LAND RECORD - VILLAGE FORM 7/12 EXTRACT",
    [
        "State: Maharashtra | District: Pune | Taluka: Haveli | Village: Shirur",
        "--------------------------------------------------------------------------------",
        "Survey / Gat Number: 142/2A",
        "Khata Number: 00482",
        "Landowner Name: Ramesh Tukaram Patil (रिमेश तुकाराम पाटील)",
        "Joint Owner: Suresh Tukaram Patil (सुरेश तुकाराम पाटील)",
        "Cultivable Area: 1.4500 Hectares",
        "Total Plot Area: 1.5000 Hectares",
        "Land Classification: Class-1 Agricultural",
        "Encumbrance: Bank of Maharashtra Agri Loan - INR 2,00,000"
    ]
)

# Generate Sample 2: Hindi Khasra
create_document_image(
    "sample_hindi_khasra.png",
    "UTTAR PRADESH BHULEKH - KHASRA KHATAUNI EXTRACT (FORM B-1)",
    [
        "State: Uttar Pradesh | District: Varanasi | Tehsil: Sadar | Village: Rampur",
        "--------------------------------------------------------------------------------",
        "Khasra Number: 318/1",
        "Khata Number: 00195",
        "Landowner Name: Rajesh Kumar Singh (राजेश कुमार सिंह)",
        "Father's Name: Ramnaresh Singh",
        "Total Area: 0.8250 Hectares",
        "Land Classification: Sankramaniya Bhumidhar (Agricultural)",
        "Annual Tax: INR 42.50",
        "Status: Mutation Order No. 2024/09/12 Verified"
    ]
)

# Generate Sample 3: English RoR
create_document_image(
    "sample_english_ror.png",
    "REVENUE DEPARTMENT - RECORD OF RIGHTS & TITLE CERTIFICATE",
    [
        "State: Karnataka | District: Belagavi | Taluk: Chikodi | Village: Nipani",
        "--------------------------------------------------------------------------------",
        "Survey Number: 87/3B",
        "Khata Number: 10452",
        "Landowner Name: Anand Mallappa Desai",
        "Co-Owner: Sunita Anand Desai",
        "Total Plot Area: 2.1500 Hectares",
        "Land Classification: Dry Agricultural Land",
        "Assessment Tax: INR 120.00",
        "Encumbrance Status: NIL (Clear Marketable Title)"
    ]
)

# Generate Sample 4: Faded / Degraded Document
create_document_image(
    "sample_faded_record.png",
    "DAMAGED ARCHIVAL REGISTER - 1984",
    [
        "State: Maharashtra | District: Solapur | Taluka: [UNREADABLE] | Village: B...li",
        "--------------------------------------------------------------------------------",
        "Survey Number: 4? / 1",
        "Khata Number: 92",
        "Landowner Name: Vi...nath Ba... Pawar (वि...वनाथ बा... पवार)",
        "Total Plot Area: 0.???? Hectares [CORNER DAMAGED]",
        "Status: Illegible Record Entry - Verification Required"
    ],
    is_faded=True
)