    # Create a new PDF file
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle, Paragraph
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import db

try:
    xcom=db.loadcom()
except:
    xcom=["IMPEX CORPORATION WEIGH BRIDGE",
            "Ispat Nadar, Vyapar Nagar, Kanpur",
            "Mo. : 9719095897, 9839347986",
            "Graphics Printer",
            "Disable",
            1,
            2,
            ""
            "COM1",
            19200,
            "",
            5]

CN=xcom[1]
A_1=xcom[2]
A_2=xcom[3]

def generate_pdf_report(data,total_tickets, total_net_weight, total_charges):
    # Create a PDF document

    today=datetime.datetime.today()
    xdate=today.strftime("%d-%m-%y , %H:%M")
    styles = getSampleStyleSheet()
    style_title = styles["Title"]
    style_table_header = styles["Heading3"]
    style_table_header.alignment = TA_CENTER
    style_table_data = styles["BodyText"]
    address_style = ParagraphStyle(
        "AddressStyle", parent=style_table_data, fontSize=8, textColor=colors.black, alignment=TA_CENTER)


    doc = SimpleDocTemplate("report.pdf", pagesize=A4,topMargin=0.3 * inch,bottomMargin=0.3 * inch)

    # Create a list to store the data for the table
    story = []
    story.append(Paragraph(CN, style_title))
    story.append(Paragraph(A_1, style_table_header))
    story.append(Paragraph(A_2, style_table_header))
    story.append(Paragraph(xdate, address_style))
    story.append(Spacer(1, 0.2 * inch))



    table_data=[]
    # Add headers to the table
    headers = [ "Ticket\nNo.", "Vehicle\nNo.", "Vehicle\nType", "Party\nName", "Charges\nRs.", "Material",
               "Gross\nWeight\nKg", "Tare\nWeight\nKg", "Gross\nWeight\nDate", "Gross\nWeight\nTime",
               "Tare\nWeight\nDate", "Tare\nWeight\nTime", "G/T/F", "Net\nWeight\nKg"]
    table_data.append(headers)

    # Add data to the table
    for row in data:
        table_data.append(row[0:14])

    summary = [total_tickets, "", "", "", "", "", "", "", "", "", "", "", "", ""]
    table_data.append(summary)
    summary = [total_net_weight, "", "", "", "", "", "", "", "", "", "", "", "", ""]
    table_data.append(summary)
    summary = [total_charges, "", "", "", "", "", "", "", "", "", "", "", "", ""]
    table_data.append(summary)



    # Create the table and set its style
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgoldenrodyellow),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ('FONTSIZE', (0, -3), (-1, -1), 12),
        ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -3), (-1, -1), colors.lightgoldenrodyellow),
        ('SPAN', (0, -3), (-1, -3)),
        ('SPAN', (0, -2), (-1, -2)),  # Merge the second-to-last row
        ('SPAN', (0, -1), (-1, -1))

    ]))

    # Add an empty row before the summary section
    story.append(table)

    # Build the PDF document with the table
    doc.build(story, onFirstPage=lambda canvas, doc: canvas.drawString(inch, 10*inch, ""), onLaterPages=lambda canvas, doc: canvas.drawString(inch, 10*inch,""))
