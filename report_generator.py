# -*- coding: utf-8 -*-
"""
MediMind PDF Report Generator
Generates MCI-compliant X-ray analysis reports
"""

from fpdf import FPDF
from datetime import datetime
import os

class MediMindPDF(FPDF):
    """Custom PDF class with MediMind branding"""
    
    def header(self):
        """Add header to each page"""
        self.set_font('Arial', 'B', 16)
        self.set_text_color(33, 150, 243)  # Blue color
        self.cell(0, 10, 'MEDIMIND AI X-RAY REPORT', 0, 1, 'C')
        self.set_text_color(0, 0, 0)  # Reset to black
        self.set_font('Arial', 'I', 10)
        self.cell(0, 6, 'AI-Assisted Medical Decision Support System', 0, 1, 'C')
        self.ln(5)
        
        # Horizontal line
        self.set_draw_color(33, 150, 243)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)
    
    def footer(self):
        """Add footer to each page"""
        self.set_y(-20)
        
        # Horizontal line
        self.set_draw_color(33, 150, 243)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)
        
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 5, f'Generated: {datetime.now().strftime("%d/%m/%Y %H:%M")} | MCI Decision Support Only | Not a substitute for clinical judgment', 0, 0, 'C')
        self.ln(5)
        self.cell(0, 5, f'Page {self.page_no()}', 0, 0, 'C')
    
    def section_title(self, title, icon=''):
        """Add a section title"""
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(240, 240, 240)
        # Remove emoji from title
        clean_title = ''.join(c for c in title if ord(c) < 128)
        self.cell(0, 8, f'{clean_title}', 0, 1, 'L', True)
        self.ln(2)
    
    def section_content(self, content):
        """Add section content"""
        self.set_font('Arial', '', 10)
        # Remove emojis and non-ASCII characters
        clean_content = ''.join(c if ord(c) < 128 else '?' for c in content)
        self.multi_cell(0, 6, clean_content)
        self.ln(3)

def generate_pdf(report_data, output_path):
    """
    Generate PDF report from analysis data
    
    Args:
        report_data (dict): Report information
            - patient_name: str
            - age: int
            - village: str
            - symptoms: str
            - diseases_detected: list or str
            - confidence_scores: dict or str
            - ai_report: str
            - doctor_notes: str
            - hindi_patient: str
            - doctor_name: str
            - doctor_mci: str
            - doctor_phc: str
            - scan_date: str (optional)
        output_path (str): Path to save PDF
    
    Returns:
        str: Path to generated PDF
    """
    
    # Create PDF
    pdf = MediMindPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=25)
    
    # Patient Information Section
    pdf.section_title('PATIENT INFORMATION', '👤')
    
    patient_info = f"""Name: {report_data.get('patient_name', 'N/A')}
Age: {report_data.get('age', 'N/A')} years
Village: {report_data.get('village', 'N/A')}
Symptoms: {report_data.get('symptoms', 'N/A')}
Scan Date: {report_data.get('scan_date', datetime.now().strftime('%d/%m/%Y'))}"""
    
    pdf.section_content(patient_info)
    
    # AI Scan Results Section
    pdf.section_title('AI SCAN RESULTS', '📊')
    
    diseases = report_data.get('diseases_detected', [])
    if isinstance(diseases, list):
        diseases_text = '\n'.join([f"• {d}" for d in diseases])
    else:
        diseases_text = str(diseases)
    
    if not diseases_text.strip():
        diseases_text = "No significant findings detected"
    
    pdf.section_content(diseases_text)
    
    # Confidence Scores (if available)
    confidence = report_data.get('confidence_scores', {})
    if confidence:
        pdf.set_font('Arial', 'I', 9)
        if isinstance(confidence, dict):
            conf_text = ', '.join([f"{k}: {v}" for k, v in confidence.items()])
        else:
            conf_text = str(confidence)
        pdf.multi_cell(0, 5, f"Confidence: {conf_text}")
        pdf.ln(3)
    
    # AI Clinical Analysis Section
    pdf.section_title('AI CLINICAL ANALYSIS', '🔍')
    
    ai_report = report_data.get('ai_report', 'No AI analysis available')
    # Limit to 800 characters to fit on page
    if len(ai_report) > 800:
        ai_report = ai_report[:800] + "..."
    
    pdf.section_content(ai_report)
    
    # Doctor's Assessment Section
    pdf.section_title('DOCTOR\'S ASSESSMENT', '👨‍⚕️')
    
    doctor_info = f"""Doctor: {report_data.get('doctor_name', 'N/A')}
MCI Registration: {report_data.get('doctor_mci', 'N/A')}
PHC: {report_data.get('doctor_phc', 'N/A')}

Notes:
{report_data.get('doctor_notes', 'No additional notes')}"""
    
    pdf.section_content(doctor_info)
    
    # Hindi Patient Report Section (if available)
    hindi_report = report_data.get('hindi_patient', '')
    if hindi_report and hindi_report.strip():
        pdf.section_title('Hindi Report (Patient Copy)', '')
        
        # Note: FPDF doesn't support Hindi fonts - show placeholder
        pdf.set_font('Arial', 'I', 9)
        pdf.multi_cell(0, 6, "[Hindi translation available - requires Unicode font support for display]")
        pdf.ln(3)
    
    # Disclaimer Section
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 9)
    pdf.set_text_color(200, 0, 0)
    pdf.cell(0, 6, 'IMPORTANT DISCLAIMER:', 0, 1)
    pdf.set_font('Arial', '', 8)
    pdf.set_text_color(0, 0, 0)
    
    disclaimer = """This report is generated by AI-assisted analysis and is intended for decision support only. 
It should not be considered as a final diagnosis. Clinical correlation and physician judgment are essential. 
This report complies with MCI guidelines for telemedicine and AI-assisted diagnosis."""
    
    pdf.multi_cell(0, 5, disclaimer)
    
    # Save PDF
    pdf.output(output_path)
    
    return output_path

def upload_pdf_to_supabase(pdf_path, supabase_client, bucket_name='reports'):
    """
    Upload PDF to Supabase Storage
    
    Args:
        pdf_path (str): Local path to PDF file
        supabase_client: Supabase client instance
        bucket_name (str): Storage bucket name
    
    Returns:
        str: Public URL of uploaded PDF
    """
    try:
        # Read PDF file
        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()
        
        # Generate unique filename
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.path.basename(pdf_path)}"
        
        # Upload to Supabase Storage
        # Note: This is a stub - actual implementation depends on Supabase storage setup
        # For now, return a placeholder URL
        
        # In production:
        # result = supabase_client.storage.from_(bucket_name).upload(filename, pdf_data)
        # public_url = supabase_client.storage.from_(bucket_name).get_public_url(filename)
        
        # Placeholder URL
        public_url = f"https://your-project.supabase.co/storage/v1/object/public/{bucket_name}/{filename}"
        
        return public_url
    
    except Exception as e:
        print(f"Error uploading PDF: {e}")
        return None

def generate_and_upload(report_data, supabase_client=None):
    """
    Generate PDF and upload to Supabase in one step
    
    Args:
        report_data (dict): Report information
        supabase_client: Supabase client instance (optional)
    
    Returns:
        tuple: (local_path, public_url)
    """
    # Create reports directory if it doesn't exist
    os.makedirs('reports', exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    patient_name = report_data.get('patient_name', 'patient').replace(' ', '_')
    filename = f"{timestamp}_{patient_name}_report.pdf"
    local_path = os.path.join('reports', filename)
    
    # Generate PDF
    generate_pdf(report_data, local_path)
    
    # Upload to Supabase (if client provided)
    public_url = None
    if supabase_client:
        public_url = upload_pdf_to_supabase(local_path, supabase_client)
    
    return local_path, public_url

# Test function
if __name__ == "__main__":
    # Test PDF generation
    test_data = {
        'patient_name': 'Ramesh Patel',
        'age': 45,
        'village': 'Anklav',
        'symptoms': 'Cough for 5 days, chest pain',
        'diseases_detected': ['Pneumonia (92%)', 'Cardiomegaly (78%)', 'Effusion (65%)'],
        'confidence_scores': {'Pneumonia': '92%', 'Cardiomegaly': '78%'},
        'ai_report': '''Based on the X-ray analysis, the following findings are noted:

1. PNEUMONIA (ICD-10: J18.9): High confidence detection of consolidation in the right lower lobe, consistent with bacterial pneumonia. Recommend sputum culture and antibiotic therapy.

2. CARDIOMEGALY: Enlarged cardiac silhouette noted. Cardiothoracic ratio appears elevated. Recommend ECG and echocardiography for further evaluation.

3. PLEURAL EFFUSION: Small amount of fluid noted in the right costophrenic angle.

RECOMMENDATIONS:
- Start empirical antibiotic therapy (Amoxicillin-Clavulanate)
- Order CBC, CRP, ESR
- ECG and chest X-ray follow-up in 7 days
- Consider referral to pulmonologist if no improvement

URGENCY: MEDIUM - Start treatment within 24 hours''',
        'doctor_notes': '''Patient examined. Clinical findings consistent with AI analysis.

Treatment Plan:
1. Tab. Amoxicillin-Clavulanate 625mg TDS x 7 days
2. Tab. Paracetamol 500mg SOS for fever
3. Syrup Salbutamol 5ml TDS for cough
4. Advised rest and adequate hydration
5. Follow-up in 3 days or if symptoms worsen

Patient counseled about medication compliance and warning signs.''',
        'hindi_patient': '''मरीज की जांच में निमोनिया (फेफड़ों में संक्रमण) पाया गया है।

दवाइयां:
1. एमोक्सिसिलिन की गोली - दिन में 3 बार, 7 दिन तक
2. बुखार के लिए पैरासिटामोल
3. खांसी की दवा

सलाह:
- आराम करें और पानी पीते रहें
- दवाई समय पर लें
- 3 दिन बाद फिर से दिखाएं
- अगर तबीयत ज्यादा खराब हो तो तुरंत आएं''',
        'doctor_name': 'Dr. Rajesh Shah',
        'doctor_mci': 'GJMC12345',
        'doctor_phc': 'Anklav PHC',
        'scan_date': '28/02/2026'
    }
    
    # Generate PDF
    os.makedirs('reports', exist_ok=True)
    output_path = 'reports/test_report.pdf'
    
    print("Generating test PDF...")
    generate_pdf(test_data, output_path)
    print(f"✅ PDF generated: {output_path}")
    print(f"File size: {os.path.getsize(output_path)} bytes")
