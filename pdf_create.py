from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer


def create_patient_discharge_pdf(filename, patient_info, discharge_summary, dispensary_info):

	doc = SimpleDocTemplate(filename, pagesize=A4)
	elements = []


	styles = getSampleStyleSheet()
	title_style = ParagraphStyle(
		'Title',
		parent=styles['Title'],
		fontName='Helvetica-Bold',
		fontSize=18,
		spaceAfter=14
	)


	title = Paragraph("Bemor bayonoti", title_style)
	elements.append(title)
	elements.append(Spacer(1, 12))

	dispensary_addres = ParagraphStyle(
		'Dispensary',
		parent=styles['Normal'],
		fontName='Helvetica',
		fontSize=12,
		leading=16
	)

	dispensary_name = f"""
    <b>Dispanser nomi:</b> {dispensary_info['name']}<br/>
    """

	dispensary_info_paragraph = Paragraph(dispensary_name, dispensary_addres)
	elements.append(dispensary_info_paragraph)
	elements.append(Spacer(1, 12))


	info_title_style = ParagraphStyle(
		'InfoTitle',
		parent=styles['Normal'],
		fontName='Helvetica-Bold',
		fontSize=14,
		spaceAfter=6
	)

	info_style = ParagraphStyle(
		'Normal',
		parent=styles['Normal'],
		fontName='Helvetica',
		fontSize=12,
		leading=16
	)


	patient_info_title = Paragraph("Bemor Ma'lumotlari", info_title_style)
	elements.append(patient_info_title)


	patient_info_text = f"""
    <b>ID:</b> {patient_info['id']}<br/>
    <b>Ism:</b> {patient_info['firstname']}<br/>
    <b>Familya:</b> {patient_info['lastname']}<br/>
    <b>Kelgan sana:</b> {patient_info['arrival_date']}<br/>
    <b>Dispanser ID:</b> {patient_info['dispensary_id']}<br/>
    <b>Palata raqami:</b> {patient_info['room_number']}<br/>
    <b>Yotoq raqami:</b> {patient_info['bunk_number']}<br/>
    <b>Bayonot sanasi:</b> {patient_info['date_of_statement']}<br/>
    """
	patient_info_paragraph = Paragraph(patient_info_text, info_style)
	elements.append(patient_info_paragraph)
	elements.append(Spacer(1, 12))


	summary_title = Paragraph("Yakuniy tashxis va tavsiyalar:", title_style)
	elements.append(summary_title)
	elements.append(Spacer(1, 12))


	discharge_summary_paragraph = Paragraph(discharge_summary, info_style)
	elements.append(discharge_summary_paragraph)
	elements.append(Spacer(1, 12))

	dispensary_address = ParagraphStyle(
		'Dispensary',
		parent=styles['Normal'],
		fontName='Helvetica',
		fontSize=12,
		leading=16
	)

	dispensary_address_name = f"""
	    <b>Manzil:</b> {dispensary_info['address']}<br/>
	    <b>Telefon raqami:</b> {dispensary_info['phone_number']}<br/>
	    """

	dispensary_info_paragraph = Paragraph(dispensary_address_name, dispensary_address)
	elements.append(dispensary_info_paragraph)
	elements.append(Spacer(1, 12))

	doc.build(elements)


test_patient_info = {
	"id": 12345,
	"firstname": "Abduqodir",
	"lastname": "Abduqodirov",
	"arrival_date": "01.07.2024",
	"dispensary_id": 6789,
	"room_number": 101,
	"bunk_number": 2,
	"date_of_statement": "11.07.2024",
	"name": "Medion Innovation",
	"address": "Toshkent, Abdulla Qodiriy ko'chasi 39/1",
	"phone_number": "78 120 00 33",
}

test_discharge_summary = """
Bemor gipertonik inqiroz tashxisi bilan kasalxonaga yotqizilgan.

Davolash:
Bemor antihipertenziv dorilarni qo‘llash orqali davolandi.

Tavsiyalar:

Terapiyani davom ettirish tavsiya etiladi.
Davolanish jarayonida bemor terapevt nazorati ostida bo‘lishi kerak.
Ambulatoriya asosida davolanish tavsiya etiladi.

"""

test_dispensary_info = {
	"name": "Medion Innovation",
	"address": "Toshkent shahar, Abdulla Qodiriy ko'chasi 39/1",
	"phone_number": "78 120 00 33"
}

create_patient_discharge_pdf("patient_discharge.pdf", test_patient_info, test_discharge_summary, test_dispensary_info)
