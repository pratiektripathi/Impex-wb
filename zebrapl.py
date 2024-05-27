import datetime
import os
import win32api
import win32print
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY,TA_LEFT, TA_RIGHT
import db
xcom=[]

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
            "",
            "COM1",
            19200,
            "",
            5]

CN=xcom[1]
A_1=xcom[2]
A_2=xcom[3]
P_T=xcom[4]
SWP=xcom[5]
NCPF1=xcom[6]
NCPF2=xcom[7]
DPrint=xcom[8]


def get_available_printers():
    printers = []
    for printer_name in win32print.EnumPrinters(2):  # 2 represents PRINTER_ENUM_LOCAL constant for local printers
        printers.append(printer_name[2])
    return printers

def print_ticket(data,stype,final):

    data=data
    name = CN
    address1 = A_1
    address2 = A_2
    date = datetime.date.today().strftime("%d-%m-%Y")
    slip_type = stype
    ticket_no = str(data[0])
    party_name = str(data[3])
    vehicle_no = str(data[1])
    vehicle_type = str(data[2])
    material = str(data[5])
    charges = str(data[4])
    gross_weight = str(data[6])
    gdate = str(data[8])
    gtime = str(data[9])
    tare_weight = str(data[7])
    tdate =str(data[10])
    ttime =str(data[11])
    net_weight = str(data[13])


    if gross_weight!="":
        gross_weight=gross_weight + " Kg"
    else:
        pass

    if tare_weight!="":
        tare_weight=tare_weight +" Kg"
    else:
        pass

    if net_weight!="":
        net_weight=net_weight + " Kg"
    else:
        pass



    # Create a PDF document with adjusted page size

    doc = SimpleDocTemplate("Ticket.pdf", pagesize=A4, topMargin=0.3 * inch,bottomMargin=0.3 * inch)

    # Define styles
    styles = getSampleStyleSheet()
    header_style = styles["Heading1"]
    header_style.alignment = TA_CENTER
    body_style = styles["BodyText"]

    address_style = ParagraphStyle(
        "AddressStyle", parent=body_style, fontSize=12, textColor=colors.black, alignment=TA_CENTER
    )



    # Create content for the ticket
    content = []


    content.append(Paragraph(name, header_style))
    content.append(Paragraph(address1, address_style))
    content.append(Paragraph(address2, address_style))


    spac = Spacer(1, 0.25 * inch)
    content.append(spac)


    rst_table = Table(
        [
            ["Ticket No.",":", ticket_no ,"","Date: "+date],
            ["","", "","",slip_type]
        ],
        colWidths=[0.7 * inch,0.2 * inch,  2.25 * inch, 1.7 * inch, 1 * inch],
        rowHeights=[0.2 * inch] * 2,
    )
    rst_table.setStyle(
        TableStyle(
            [
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("FONTSIZE", (1, 0), (2, -1), 12),
                ("FONTNAME", (1, 0), (2, -1), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, 0), "LEFT"),
                ("ALIGN", (0, 1), (-1, 1), "LEFT"),
                ("ALIGN", (-1, 0), (-1, -1), "RIGHT"),
                ("TOPPADDING", (0, 0), (-1, 0), 4),
                ("TOPPADDING", (0, 1), (-1, 1), 4),
                ("SPAN", (0, 0), (0, 1)),
                ("SPAN", (1, 0), (1, 1)),
                ("SPAN", (2, 0), (2, 1)),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LINEBELOW", (0, -1), (-1, -1), 1, colors.black)

            ]
        )
    )
    rst_table = Table(
        [
            [rst_table],
        ],
        colWidths=[6 * inch],
        rowHeights=[None],
        hAlign="LEFT",  # Anchor to the left side
        vAlign="BOTTOM"
    )
    content.append(rst_table)



    content.append(Spacer(1, 0.05 * inch))

    line = "-----------------------------------------------------------------------------------------------------------------------------------"



    data_table = [

        ["Party Name", ": " , party_name],
        ["Vehicle No.", ": " , vehicle_no],
        ["Vehicle Type", ": " , vehicle_type],
        ["Material", ": " , material],
        ["Charges",":", " Rs. " + charges],
    ]
    tkt_table = Table(data_table, colWidths=[1.5 * inch,0.5*inch, 3 * inch])
    tkt_table.setStyle(
        TableStyle(
            [
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),

                ("FONTNAME", (0, 0), (-1, 0), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 0), (-1, 0), 8),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
                ("TOPPADDING", (0, 1), (-1, -1), 5)
            ]
        )
    )
    content.append(tkt_table)


    content.append(Paragraph(line, body_style))


    # Weight section
    # Weight section as a table
    weight_table = Table(
        [
            ["Gross Weight",":", gross_weight, gdate, gtime],
            ["Tare Weight",":", tare_weight, tdate, ttime],

        ],
        colWidths=[1.2 * inch,0.5 * inch,  1.5 * inch, 1 * inch, 1 * inch],
        rowHeights=[0.3 * inch] * 2,
    )
    weight_table.setStyle(
        TableStyle(
            [
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("FONTSIZE", (0, 0), (2, -1), 12),
                ("FONTNAME",(0, 0), (2, -1), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, 0), "LEFT"),
                ("ALIGN", (0, 1), (-1, 1), "LEFT"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 4),
                ("TOPPADDING", (0, 0), (-1, 0), 4),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 4),
                ("TOPPADDING", (0, 1), (-1, 1), 4)

            ]
        )
    )
    weight_table = Table(
        [
            [weight_table],
        ],
        colWidths=[5 * inch],
        rowHeights=[None],
        hAlign="LEFT",  # Anchor to the left side
    )

    content.append(weight_table)
    content.append(Paragraph(line, body_style))



    # Net weight section

    net_weight_table = Table(
        [
            ["Net Weight",":", net_weight,"","Operator Sign."],
            ["","", "","","User Name: Admin"]
        ],
        colWidths=[1.2 * inch,0.5 * inch,  2.2 * inch, 1 * inch, 1 * inch],
        rowHeights=[0.3 * inch] * 2,
    )
    net_weight_table.setStyle(
        TableStyle(
            [
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("FONTSIZE", (0, 0), (2, -1), 16),
                ("FONTNAME", (0, 0), (2, -1), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (2, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, 0), "LEFT"),
                ("ALIGN", (0, 1), (-1, 1), "LEFT"),
                ("ALIGN", (-1, 0), (-1, -1), "RIGHT"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 4),
                ("TOPPADDING", (0, 0), (-1, 0), 4),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 4),
                ("TOPPADDING", (0, 1), (-1, 1), 4),
                ("SPAN", (0, 0), (0, 1)),
                ("SPAN", (1, 0), (1, 1)),
                ("SPAN", (2, 0), (2, 1)),


            ]
        )
    )
    net_weight_table = Table(
        [
            [net_weight_table],
        ],
        colWidths=[6 * inch],
        rowHeights=[None],
        hAlign="LEFT",  # Anchor to the left side
    )
    content.append(net_weight_table)

    content.append(Spacer(1, 0.2 * inch))

 # Add images to the document
    images = [f"camera/front/{ticket_no}_1.jpg", f"camera/back/{ticket_no}_1.jpg", f"camera/front/{ticket_no}_2.jpg", f"camera/back/{ticket_no}_2.jpg"]  # Replace with your image paths
    image_table_data = []
    for image in images:
        if os.path.exists(image):
            img = Image(image)
            img.drawWidth = 2.25 * inch
            img.drawHeight = 2.25 * inch
            image_table_data.append([img])
        else:
            img = Image("res/blank.jpg")
            img.drawWidth = 2.25 * inch
            img.drawHeight = 2.25 * inch
            image_table_data.append([img])

    image_table = Table(
        [image_table_data[:2], image_table_data[2:]],
        colWidths=[2.5 * inch, 2.5 * inch],
        rowHeights=[2.5 * inch, 2.5 * inch]
    )
    image_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black)
            ]
        )
    )

    content.append(image_table)







    if SWP=="Enable":
        doc.build(content + [Spacer(1,0.3 * inch)] + content)
    else:
        doc.build(content)


    if DPrint=="":
        printer_name = win32print.GetDefaultPrinter()
    else:
        printer_name = DPrint

    if final=="F":
        for x in range(int(NCPF2)):
            win32api.ShellExecute(0, "print", "Ticket.pdf", f'"{printer_name}"', ".", 0)
    else:
        for x in range(int(NCPF1)):
            win32api.ShellExecute(0, "print", "Ticket.pdf", f'"{printer_name}"', ".", 0)






