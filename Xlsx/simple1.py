# -*- coding: utf-8 -*-
import xlsxwriter

workbook = xlsxwriter.Workbook('demo1.xlsx')  # 创建一个Excel文件
sheet1 = workbook.add_worksheet(name='sheet1')  # 创建一个工作表对象

sheet1.set_column('A:A', 20)  # 设定A列宽度为20像素
bold = workbook.add_format({'bold': True})  # 定义一个加粗的格式对象

sheet1.write('A1', 'Hello')  # A1 单元格写入'Hello'
sheet1.write('A2', 'World', bold)
sheet1.write('B2', '中文测试', bold)

sheet1.write(2, 0, 32)  # 用行列表示法写入数字'32'和'35.5'
sheet1.write(3, 0, 35.5)  # 以0为index的起始值
sheet1.write(4, 0, '=SUM(A3:A4)')  # 求A3:A4的和, 并将结果写入A5

sheet1.insert_image('B5', './img.jpg')
workbook.close()
