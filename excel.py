import openpyxl
from openpyxl import Workbook
import os


def add_data_to_excel(data):
    file = "data.xlsx"
    if not os.path.exists(file):
        wb = Workbook()
        ws = wb.active
    else:
        wb = openpyxl.load_workbook(file)
        ws = wb.active
    ws.append(data)
    wb.save(file)