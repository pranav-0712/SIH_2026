from PIL import Image, ImageDraw, ImageFont
import os

def draw_satbara(filename, doc_data, is_faded=False):
    width, height = 1000, 750
    bg = (248, 244, 230) if is_faded else (255, 255, 255)
    text_color = (120, 120, 120) if is_faded else (20, 20, 20)
    grid_color = (160, 150, 130) if is_faded else (60, 60, 60)
    
    img = Image.new("RGB", (width, height), color=bg)
    draw = ImageDraw.Draw(img)
    
    # Outer formal double border
    draw.rectangle([15, 15, width - 15, height - 15], outline=grid_color, width=2)
    draw.rectangle([20, 20, width - 20, height - 20], outline=grid_color, width=1)
    
    # Header box
    draw.rectangle([25, 25, width - 25, 110], outline=grid_color, width=2)
    draw.text((320, 35), "महाराष्ट्र शासन - महसूल विभाग (GOVT. OF MAHARASHTRA)", fill=text_color)
    draw.text((280, 58), "गाव नमुना ७ (अधिकार अभिलेख पत्रक) आणि गाव नमुना १२ (पिकांची पाहणी)", fill=text_color)
    
    # Village Meta Header
    meta_line = f"गाव (Village): {doc_data['village']}  |  तालुका (Taluka): {doc_data['tehsil']}  |  जिल्हा (District): {doc_data['district']}"
    draw.text((180, 85), meta_line, fill=text_color)
    
    # Table Grid (Form 7 - Adhikar Abhilekh)
    draw.rectangle([25, 115, width - 25, 480], outline=grid_color, width=2)
    
    # Vertical Column Dividers
    draw.line([(180, 115), (180, 480)], fill=grid_color, width=2) # Col 1: Survey/Gat
    draw.line([(340, 115), (340, 480)], fill=grid_color, width=2) # Col 2: Area
    draw.line([(700, 115), (700, 480)], fill=grid_color, width=2) # Col 3: Kabjedar/Owner
    # Col 4: Other Rights (700 to end)
    
    # Header Row
    draw.line([(25, 155), (width - 25, 155)], fill=grid_color, width=2)
    draw.text((35, 125), "भूमापन / गट क्र.\n(Survey / Gat No)", fill=text_color)
    draw.text((195, 125), "क्षेत्र (हेक्टर.आर)\n(Total Area Ha)", fill=text_color)
    draw.text((360, 125), "खातेदार व भोगवटादार तपशील\n(Landowner & Khata Details)", fill=text_color)
    draw.text((715, 125), "इतर हक्क व बोजा\n(Other Rights & Loans)", fill=text_color)
    
    # Cell Data
    draw.text((45, 175), f"गट क्र. {doc_data['gat_no']}", fill=text_color)
    draw.text((45, 205), f"खाते क्र. {doc_data['khata_no']}", fill=text_color)
    
    draw.text((195, 175), f"लागवडी: {doc_data['cultivable']} Ha", fill=text_color)
    draw.text((195, 205), f"पोटखराबा: {doc_data['potkharaba']} Ha", fill=text_color)
    draw.text((195, 245), f"एकूण: {doc_data['total_area']} Ha", fill=text_color)
    
    # Owner entries
    y_owner = 175
    for o in doc_data['owners']:
        draw.text((355, y_owner), f"• {o}", fill=text_color)
        y_owner += 28
        
    # Encumbrances
    draw.text((715, 175), doc_data['loans'], fill=text_color)
    draw.text((715, 230), f"फेरफार क्र. (Mutation): {doc_data['ferfar']}", fill=text_color)
    
    # Lower Section: Form 12 (Crops)
    draw.rectangle([25, 490, width - 25, height - 70], outline=grid_color, width=2)
    draw.text((35, 500), "गाव नमुना १२ - पिकांची नोंदवही (CROP INSPECTION REGISTER)", fill=text_color)
    draw.line([(25, 530), (width - 25, 530)], fill=grid_color, width=1)
    draw.text((45, 545), f"हंगाम: खरीप / रब्बी | पिकाचे नाव: {doc_data['crop']} | ओलिताचे साधन: विहीर / कालवा", fill=text_color)
    
    # Seal & Signature
    seal_color = (170, 40, 40) if not is_faded else (180, 160, 160)
    draw.ellipse([width - 220, height - 150, width - 80, height - 35], outline=seal_color, width=2)
    draw.text((width - 200, height - 105), "तलाठी / डिजिटल सही\nMAHABHULEKH", fill=seal_color)
    
    img.save(filename)
    print(f"✅ Generated: {filename}")

# --- Sample 1: Pune Satbara (High Quality Printed) ---
draw_satbara("satbara_sample_pune.png", {
    "village": "Wagholi (वाघोली)",
    "tehsil": "Haveli (हवेली)",
    "district": "Pune (पुणे)",
    "gat_no": "248/1A",
    "khata_no": "00841",
    "cultivable": "1.3500",
    "potkharaba": "0.0500",
    "total_area": "1.4000",
    "owners": [
        "रवींद्र महादेव गायकवाड (Ravindra Mahadev Gaikwad)",
        "संगीता रवींद्र गायकवाड (Sangeeta Ravindra Gaikwad)"
    ],
    "loans": "बँक ऑफ महाराष्ट्र कृषी कर्ज\nरु. ३,५०,००० बोजा नोंद.",
    "ferfar": "4892, 5104",
    "crop": "ऊस (Sugarcane) - 1.20 Ha"
})

# --- Sample 2: Nashik Satbara (Multi-Owner) ---
draw_satbara("satbara_sample_nashik.png", {
    "village": "Panchavati (पंचवटी)",
    "tehsil": "Nashik (नाशिक)",
    "district": "Nashik (नाशिक)",
    "gat_no": "112/3",
    "khata_no": "00329",
    "cultivable": "2.1000",
    "potkharaba": "0.1500",
    "total_area": "2.2500",
    "owners": [
        "दिलीप एकनाथ शिंदे (Dilip Eknath Shinde) - 1/2",
        "संतोष एकनाथ शिंदे (Santosh Eknath Shinde) - 1/2"
    ],
    "loans": "निरंक (NIL - No Encumbrances)",
    "ferfar": "1820",
    "crop": "द्राक्षे (Grapes) / कांदा (Onion)"
})

# --- Sample 3: Degraded Faded Satbara (For Testing HITL Review) ---
draw_satbara("satbara_sample_faded_review.png", {
    "village": "B...li (बारामती ग्रामीण)",
    "tehsil": "Baramati",
    "district": "Pune",
    "gat_no": "89/?",
    "khata_no": "44",
    "cultivable": "0.????",
    "potkharaba": "0.0200",
    "total_area": "0.9500",
    "owners": [
        "वि...ल बा... जगताप (Vi...l Ba... Jagtap)",
        "[कागद फाटलेला / Torn Entry]"
    ],
    "loans": "सोसायटी कर्ज नोंद अस्पष्ट...",
    "ferfar": "921 [Faded]",
    "crop": "बाजरी (Pearl Millet)"
}, is_faded=True)