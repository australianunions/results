from pathlib import Path


def save_xlsx(sheet_mapping, destination):
    destination = Path(destination).expanduser()
    from xlsxwriter import Workbook

    workbook = Workbook(str(destination))

    for name, rows in sheet_mapping.items():
        worksheet = workbook.add_worksheet(name)

        for r, row in enumerate([rows.keys()] + rows):
            for c, col in enumerate(row):
                worksheet.write(r, c, col)

    workbook.close()
