import sys

from pdftranslate.parser import Parser
from pdftranslate.translator import Translator
from pdftranslate.printer import Printer, line_height_partial
from pdftranslate.terminal import Terminal

src_path = './temp/test01.pdf'
dest_path = './temp/output.html'

dest_type = 'html'

terminal = Terminal(dest_path)


def call_terminal():
    terminal.finish_translated()


try:
    parser = Parser(src_path)
    pages = parser.get_pages()

    # if dest_type == 'txt':
    #
    # elif dest_type == 'html':
    #
    # else:
    #     terminal.show_error('不支持的目标类型！')
    #     sys.exit(1)

    printer = Printer(dest_path, title=parser.get_title())

    translator = Translator()

    text_filter = line_height_partial(max=36)

    # 由于 pages 是 generator，无法获取长度，因此先全部读取到内存中
    stored_pages = []
    for page in pages:
        stored_pages.append(page)
    terminal.set_page_count(len(stored_pages))

    terminal.show_begin()

    count = 0
    for page in stored_pages:
        parsed_layout = parser.parse_page(page)

        terminal.begin_page(parsed_layout.get_translated_count())

        translator.translate_layout(parsed_layout, 'en', 'zh-CN', call_terminal)
        printer.print_html_page(parsed_layout, text_filter=text_filter)
        count += 1
        if count > 1:
            break
    printer.save()
except Exception as e:
    terminal.show_error(repr(e))
    sys.exit(1)

terminal.show_end()

# TODO: 针对于具体错误进行处理
# TODO: 补全对于jpeg image 的处理
# TODO: 添加 hover 显示全文等功能
# TODO: 纯文本处理
# TODO: 打包成 exe
# TODO: 一个 textbox 内部可能有一个复杂的相对位置的结构，同时看起来在同一个 box 内部的文字可能会分在两个部分，导致出现遮挡问题
# TODO: 竖排文字的处理，可能还有旋转之类的操作。。。

# try:
#     parser = Parser(src_path)
#     pages = parser.get_pages()
#     printer = Printer(dest_path)
#
#     translator = Translator()
#
#     text_filter = line_height_partial(max=30)
#
#     # 由于 pages 是 generator，无法获取长度，因此先全部读取到内存中
#     stored_pages = []
#     for page in pages:
#         stored_pages.append(page)
#     terminal.set_page_count(len(stored_pages))
#
#     terminal.show_begin()
#
#     count = 0
#     for page in stored_pages:
#         parsed_layout = parser.parse_page(page)
#
#         terminal.begin_page(parsed_layout.get_translated_count())
#
#         translator.translate_layout(parsed_layout, 'en', 'zh-CN', call_terminal)
#         printer.print_page(parsed_layout, text_filter=text_filter)
#         count += 1
#         if count > 1:
#             break
#     printer.save()
#
# except Exception as e:
#     terminal.show_error(repr(e))
#     sys.exit(1)
