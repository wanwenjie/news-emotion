# -*- coding: utf-8 -*-
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBoxHorizontal
from pdfminer.pdfinterp import PDFTextExtractionNotAllowed, PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfparser import PDFDocument, PDFParser
import os
from DAF import DFAFilter

TRADE_LIST = [u"贸易", u"出口", u"关税协定/关贸总协定",
              u"贸易壁垒", u"自由贸易协定/FTA", u"投资协定",
              u"世界贸易组织/WTO", u"关税", u"经常账户", u"贸易顺差/贸易盈余/贸易赤字",
              u"中国制造", u"出口/进口许可"]


PDF_PATH = "/Users/wanwenjie/projects/news-emotion/reports/"


def filter_text(content):
    """
    过滤文本，只返回包含贸易词汇
    """
    daf = DFAFilter()
    daf.parse_list(TRADE_LIST)
    return daf.is_contain(content)


def format_text(content):
    """
    格式化提取文本，转化成list
    """
    # 以中文句号分隔
    info_list = content.split("。")
    return info_list


def parse(path):
    fp = open(path, 'rb')   # 以二进制读模式打开
    praser = PDFParser(fp)
    # 创建一个PDF文档
    doc = PDFDocument()
    # 连接分析器 与文档对象
    praser.set_document(doc)
    doc.set_parser(praser)

    # 提供初始化密码
    # 如果没有密码 就创建一个空的字符串
    doc.initialize()
    four = []
    # 检测文档是否提供txt转换，不提供就忽略
    if not doc.is_extractable:
        raise PDFTextExtractionNotAllowed
    else:
        # 创建PDf 资源管理器 来管理共享资源
        rsrcmgr = PDFResourceManager()
        # 创建一个PDF设备对象
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        # 创建一个PDF解释器对象
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        flg = False
        # 循环遍历列表，每次处理一个page的内容
        for page in doc.get_pages():  # doc.get_pages() 获取page列表
            interpreter.process_page(page)
            # 接受该页面的LTPage对象
            layout = device.get_result()
            for x in layout:
                if isinstance(x, LTTextBoxHorizontal):
                    outputtxt = str(fp.name).replace("pdf", "txt").replace("年报摘要_", "")
                    with open(outputtxt, 'a') as f:
                        results = x.get_text()
                        if layout.pageid != 3 and results.count("第四节 经营情况讨论与分析") == 1:
                            flg = True
                            print(results + '\n')
                        if layout.pageid != 3 and results.count("第五节") == 1:
                            flg = False
                        if flg:
                            four.append(results + '\n')
                        try:
                            f.write(results.replace('•', '.') + '\n')
                        except BaseException as e:
                            print("write error")
                            print(e)
    fp.close()
    f.close()
    return four


def dir(path):
    for folderName, subfolders, filenames in os.walk(path):
        print('The current folder is ' + folderName)
        for subfolder in subfolders:
            print('SUBFOLDER OF ' + folderName + ': ' + subfolder)
        for filename in filenames:
            print('FILE INSIDE ' + folderName + ': ' + filename)


def run(path):
    file_names = os.listdir(path)
    for file in file_names:
        if file.lower().count('.pdf') == 1:
            try:
                fullfname = path + file
                outputtxt = path + "Extract-" + file.lower().replace("pdf", "txt")
                if not os.path.exists(outputtxt):
                    four = parse(fullfname)
                    if len(four) > 0 and filter_text("".join(four)):
                        with open(outputtxt, 'a') as f:
                            f.writelines(four)
                f.close()
            except BaseException as e:
                print(e)


if __name__ == '__main__':
    run(PDF_PATH)
