from reportlab.pdfgen import canvas

pdf = canvas.Canvas("test_notice.pdf")

pdf.setFont("Helvetica", 14)
pdf.drawString(50, 800, "INCOME TAX DEPARTMENT")

pdf.setFont("Helvetica", 12)
pdf.drawString(50, 770, "NOTICE")
pdf.drawString(50, 740, "Notice Number: IT-2026-45821")
pdf.drawString(50, 710, "You are required to respond to this notice by 15 October 2026.")
pdf.drawString(50, 680, "Amount due: Rs. 5,000")

pdf.drawString(50, 640, "Required action:")
pdf.drawString(70, 615, "1. Respond to this notice.")
pdf.drawString(70, 590, "2. Pay the amount due.")

pdf.drawString(50, 550, "Required document:")
pdf.drawString(70, 525, "Copy of PAN card")

pdf.drawString(
    50,
    485,
    "If you do not respond by the deadline, further action may be taken."
)

pdf.drawString(
    50,
    455,
    "You can respond through the Income Tax portal."
)

pdf.save()

print("test_notice.pdf created successfully.")