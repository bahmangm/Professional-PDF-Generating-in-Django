import os
from django.http import HttpResponse

from django.conf import settings

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (Table, TableStyle, Paragraph, Spacer, Frame,
                                PageTemplate, BaseDocTemplate, FrameBreak)


class TwoColumnDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)

        # Reduce left & right margins from default(72)  → 20
        reduced_margin = 20

        # Define new page width excluding reduced margins
        available_width = letter[0] - (2 * reduced_margin)

        # Define column width
        space_between_columns = 10
        column_width = (available_width / 2) - space_between_columns
        left_column_width = column_width + 40
        right_column_width = column_width - 40

        # Define frames for left and right columns
        frame_left = Frame(reduced_margin,
                           self.bottomMargin,
                           left_column_width,
                           self.height,
                           id='left')
        frame_right = Frame(reduced_margin + left_column_width + space_between_columns,
                            self.bottomMargin,
                            right_column_width,
                            self.height,
                            id='right')

        # Assign frames to PageTemplate
        template = PageTemplate(id='TwoColumns', frames=[frame_left, frame_right])
        self.addPageTemplates([template])


def generate_pdf(pay_slip):

    # Create a response object with PDF mimetype
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="pay_slip.pdf"'

    # Create a PDF document with two columns
    pdf = TwoColumnDocTemplate(response, pagesize=letter)

    # Define styles
    title_style = ParagraphStyle(name='Title', fontSize=10, alignment=0)
    normal_style = ParagraphStyle(name='Normal', fontSize=8)

    # Table Style with Reduced Padding
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D8D8D8')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 1),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0.5),
        # ('GRID', (0, 0), (-1, -1), 0.2, colors.black),  # Thinner grid lines
        # Remove all borders
        ('BOX', (0, 0), (-1, -1), 0, colors.white),  # No outer border
        ('INNERGRID', (0, 0), (-1, -1), 0, colors.white),  # No inner grid
    ])

    # Left column of the pay slip page
    left_elements = [
        Paragraph("Employee Name", title_style),
        Spacer(1, 117),
    ]

    # Earnings Table (left column)
    earnings_data = [['Earnings', 'Rate', 'Current\nHours', 'Current\nPeriod',
                      'YTD\nHours', 'YTD\nAmount'],
                     ['Regular Pay', 19.00, 45.0, 855.0, 419.0, 7961.0],
                     ['Roofing', 20.00, '', 0.0, 0.0, 0.0],
                     ['Other', '', '', '', '', 10.00],
                     ['', '', '', '', '', ''],
                     ['Adjustment*', '', '', '', '', 0.00]]
    earnings_table = Table(earnings_data,
                           colWidths=[70, 30, 35, 35, 30, 60],
                           hAlign="LEFT")
    earnings_table.setStyle(table_style)
    left_elements.append(earnings_table)

    gross_data = [['Gross Earnings/Hours', 45.0, 855.0, 419.0, 7971.00]]
    gross_table = Table(gross_data,
                        colWidths=[100, 35, 35, 30, 60],
                        hAlign="LEFT")
    gross_table.setStyle(table_style)
    left_elements.append(gross_table)

    left_elements.append(Spacer(1, 60))

    pivot_hours = [['', '24-Feb', '25-Feb', '26-Feb', '27-Feb', '28-Feb'],
                   ['Address 1', 5.0, 7.5, 7.5, 7.5, None],
                   ['Address 2', 0.5, 0.5, 0.5, 0.5, 1.5],
                   ['Address 3', 3.5, None, None, None, None],
                   ['Address 4', None, 1.0, None, None, None],
                   ['Address 5', None, None, None, 1.0, None],
                   ['Address 6', None, None, 1.0, None, None],
                   ['Address 7', None, None, None, None, 1.0],
                   ['Address 8', None, None, None, None, 1.0],
                   ['Address 9', None, None, None, None, 0.5],
                   ['Address 10', None, None, None, None, 1.0],
                   ['Address 11', None, None, None, None, 2.0],
                   ['Address 12', None, None, None, None, 2.0],
                   ['Grand Total', 9.0, 9.0, 9.0, 9.0, 9.0]]
    pivot_table = Table(pivot_hours,
                        colWidths=[106, 30, 30, 30, 30, 30, 30, 30],
                        hAlign="LEFT")
    pivot_table.setStyle(table_style)
    left_elements.append(pivot_table)


    # **FRAMEBREAK: Moves next content to right column**
    left_elements.append(FrameBreak())

    # Statutory Deductions Table (right column)
    right_elements = [
        Paragraph("Company Name", normal_style),
        Paragraph("Company Address", normal_style),
        Paragraph("City, Province", normal_style),
        Paragraph("Postal Code", normal_style),
        Spacer(1, 10),
    ]

    period_data = [['Pay Period No.', '9 of 52'],
                   ['Period Beginning', '2025, 2, 24'],
                   ['Period Ending', '2025, 3, 2'],
                   ['Pay Date', '2025, 3, 7'],
                   ['Pay Period Type', 'Weekly']]
    period_table = Table(period_data, colWidths=[100, 60], hAlign="LEFT")
    second_table_style = TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        # Remove all borders
        ('BOX', (0, 0), (-1, -1), 0, colors.white),  # No outer border
        ('INNERGRID', (0, 0), (-1, -1), 0, colors.white),  # No inner grid
    ])
    period_table.setStyle(second_table_style)
    right_elements.append(period_table)
    right_elements.append(Spacer(1, 10))

    deductions_data = [['Statutory Deductions', 'Current Period', 'YTD Amount'],
                       ['Vehicle', 42.00, 294.00],
                       ['Rent', '', 0.00],
                       ['Other', '', 0.00]]
    deductions_table = Table(deductions_data,
                             colWidths=[110, 60, 70],
                             hAlign="LEFT")
    deductions_table.setStyle(table_style)
    right_elements.append(deductions_table)

    total_deductions_data = [['Total Deductions', 42.00, 294.00]]
    total_deductions_table = Table(total_deductions_data,
                                   colWidths=[110, 60, 70],
                                   hAlign="LEFT")
    total_deductions_table.setStyle(table_style)
    right_elements.append(total_deductions_table)

    net_pay_data = [['Net Pay', 813.0, 7677.00]]
    net_pay_table = Table(net_pay_data, colWidths=[110, 60, 70], hAlign="LEFT")
    net_pay_table.setStyle(table_style)
    right_elements.append(net_pay_table)

    last_rounding_data = [['Last Rounding', 0.0]]
    last_rounding_table = Table(last_rounding_data,
                                colWidths=[110, 60],
                                hAlign="LEFT")
    last_rounding_table.setStyle(table_style)
    right_elements.append(last_rounding_table)

    right_elements.append(Spacer(1, 15))

    paid_via_cash_data = [['Paid Via E_Transfer', 813.00]]
    paid_via_cash_table = Table(paid_via_cash_data,
                                colWidths=[110, 130],
                                hAlign="LEFT")
    paid_via_cash_table.setStyle(table_style)
    right_elements.append(paid_via_cash_table)

    # display the names
    right_elements.append(Spacer(1, 70))
    names_data = [
        ["Created By:", "Accountant Name"],
        ["Approved By:", "Manager Name"],
        ["Acknowledged By:", "Employee Name"],
        ]
    names_table = Table(names_data, colWidths=[100, 60], hAlign="LEFT")
    names_table.setStyle(second_table_style)
    right_elements.append(names_table)

    # Add both column elements to PDF
    pdf.build(left_elements + right_elements)

    # Save the PDF to the media directory
    pdf_filename = f"temp/pay_slip_{pay_slip.id}.pdf"
    pdf_path = os.path.join(settings.MEDIA_ROOT, pdf_filename)
    with open(pdf_path, 'wb') as f:
        f.write(response.content)

    # Return the URL to the PDF
    return os.path.join(settings.MEDIA_URL, pdf_filename)


def generate_pay_slip(request, pay_slip_id):
    pay_slip = PaySlip.objects.get(id=pay_slip_id)
    pdf_url = generate_pdf(pay_slip)
    return HttpResponseRedirect(pdf_url)
