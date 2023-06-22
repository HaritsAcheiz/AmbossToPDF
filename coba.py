from fpdf import FPDF
from selectolax.parser import HTMLParser


class PDF(FPDF):
    def html_table(self, html):
        parser = HTMLParser(html)
        table = parser.css_first("table")
        rows = table.css("thead > tr")

        # Process table header data and draw table header
        self.process_table_header(rows)

    def process_table_header(self, rows):

        # get max rows
        for row in rows:
            cells = row.css('th')
            rowspans = []
            for cell in cells:
                try:
                    rowspans.append(int(cell.attributes['rowspan']))
                except:
                    rowspans.append(1)
            for i in range(max(rowspans)):
                cells = rows[i].css('th')
                for cell in cells:
                    if cell is None:
                        # set font
                        self.set_font(family='EpocaPro', style='', size=10)

                        # Calculate cell width and height based on colspan and rowspan
                        max_width = self.w - 2 * self.l_margin
                        cell_width = max_width / 2

                        # Draw merged cell
                        self.cell(w=cell_width, h=20, txt='', border=1, align='C')
                    else:
                        colspan = int(cell.attributes.get("colspan", 1))
                        content = cell.text().strip()

                        # Calculate cell width and height based on colspan and rowspan
                        max_width = self.w - 2 * self.l_margin
                        cell_width = max_width / (colspan * 2)

                        # set font
                        self.set_font(family='EpocaPro', style='', size=10)

                        # Draw merged cell
                        self.cell(w=cell_width, h=20, txt=content, border=1, align='C')
        # main function
            self.ln()

    # def process_table_header(self, rows):
    #     for row in rows:
    #         cells = row.css("th")
    #         for cell in cells:
    #             colspan = int(cell.attributes.get("colspan", 1))
    #             rowspan = int(cell.attributes.get("rowspan", 1))
    #             content = cell.text().strip()
    #
    #             # Calculate cell width and height based on colspan and rowspan
    #             max_width = self.w - 2 * self.l_margin
    #             cell_width = max_width / (colspan * 2)
    #             cell_height = 20 * rowspan
    #
    #             scope = cell.attributes.get("scope", "")
    #             if scope.lower() == "col":
    #                 align = "C"
    #                 border = "TB"
    #             elif scope.lower() == "row":
    #                 align = "L"
    #                 border = "LR"
    #             else:
    #                 align = "C"
    #                 border = "LR"
    #
    #             #set font
    #             self.set_font(family='EpocaPro', style='', size=10)
    #
    #             # Draw merged cell
    #             self.cell(cell_width, cell_height, content, border=border, align=align)
    #
    #
    #         self.ln()

    # def process_table_header(self, rows):
    #     # Process first row
    #     first_row_cells = rows[0].css("th")
    #     for cell in first_row_cells:
    #         colspan = int(cell.attributes.get("colspan", 1))
    #         rowspan = int(cell.attributes.get("rowspan", 1))
    #         content = cell.text().strip()
    #
    #         # Calculate cell width and height based on colspan and rowspan
    #         max_width = self.w - 2 * self.l_margin
    #         cell_width = max_width / (colspan * 2)
    #         cell_height = 20 * rowspan
    #
    #         # Set font
    #         self.set_font(family='EpocaPro', style='', size=12)
    #
    #         # Set cell attributes
    #         border = 1
    #         align = "C"
    #
    #         # Draw merged cell
    #         self.cell(cell_width, cell_height, content, border=border, align=align)
    #
    #     self.ln()
    #
    #     # Process second row
    #     second_row_cells = rows[1].css("th")
    #     column_widths = []
    #     for cell in second_row_cells:
    #         colspan = int(cell.attributes.get("colspan", 1))
    #         rowspan = int(cell.attributes.get("rowspan", 1))
    #         content = cell.text().strip()
    #
    #         # Calculate cell width and height based on colspan and rowspan
    #         max_width = self.w - 2 * self.l_margin
    #         cell_width = max_width / (colspan * 2)
    #         cell_height = 20 * rowspan
    #
    #         # Set font
    #         self.set_font(family='EpocaPro', style='', size=12)
    #
    #         # Set cell attributes
    #         border = 1
    #         align = "C"
    #
    #         # Draw merged cell
    #         self.cell(cell_width, cell_height, content, border=border, align=align)
    #
    #         # Store the column width for alignment adjustment
    #         column_widths.append(cell_width)
    #
    #     self.ln()
    #
    #     # Adjust the alignment of the second row cells based on the column widths
    #     for i, width in enumerate(column_widths):
    #         if i == 0:
    #             self.set_x(self.l_margin)
    #         else:
    #             self.set_x(self.get_x() + width)
    #         self.multi_cell(width, 0, "", border="B", align="C")
    #
    #     self.ln()

# Create a new PDF object
pdf = PDF(orientation='P', unit='pt', format='A4')
pdf.add_font('EpocaPro', style='', fname='fonts/EpocaPro-Regular.ttf')
pdf.add_font('EpocaPro', style='B', fname='fonts/EpocaPro-Bold.ttf')
pdf.add_font('EpocaPro', style='I', fname='fonts/EpocaPro-Italic.ttf')
pdf.add_page()

# HTML table content
html_table = """
<table>
<thead>
<tr>
<th colspan="1" rowspan="2" scope="row"><span class="leitwort"><span class="api" data-type="anker" id="Zf986b50503189d52299b2795dd3f83be">Auskultationsbefunde nach Lokalisation des Herzgeräusches</span></span></th>
<th colspan="2" rowspan="1" scope="col"><span class="leitwort">Befund</span></th>
<th colspan="1" rowspan="2" scope="col"><span class="leitwort">Mögliche Ursachen</span></th>
</tr>
<tr>
<th scope="col"><span class="leitwort">Betroffene Struktur</span></th>
<th scope="col"><span class="leitwort">Geräusch</span></th>
</tr>
</thead>
<table>
"""

# Convert HTML table header to PDF table header
pdf.html_table(html_table)

# Output the PDF
pdf.output("output.pdf")
