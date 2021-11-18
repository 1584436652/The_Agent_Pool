from openpyxl import load_workbook


def load_table():
    wb = load_workbook('re.xlsx')
    ws = wb["整理后"]
    # ws = wb.active
    rows = []
    sku = []
    sku_dict = dict()
    for row in ws.iter_rows():
        rows.append(row)
    for x in range(1, len(rows)):
        sku_name = str(rows[x][0].value)
        billing_weight = str(rows[x][3].value)
        sku.append(billing_weight)
        sku_dict[sku_name] = sku
    print(sku_dict)


load_table()
