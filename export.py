from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

def export_pdf(data):
    doc = SimpleDocTemplate("expense_report.pdf")

    table_data = [["Category", "Total"]]

    total = 0
    for row in data:
        table_data.append([row[0], str(row[1])])
        total += row[1]

    table_data.append(["TOTAL", str(total)])

    table = Table(table_data)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,-1), (-1,-1), colors.lightgrey),
    ]))

    doc.build([table])