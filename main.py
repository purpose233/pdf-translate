import sys
import argparse

from pdftranslate.parser import Parser
from pdftranslate.translator import Translator, Supported_languages
from pdftranslate.printer import Printer, line_height_partial
from pdftranslate.terminal import Terminal

argparser = argparse.ArgumentParser(description='manual to this script')
argparser.add_argument('--src', type=str, default=None)
argparser.add_argument('--out', type=str, default=None)
argparser.add_argument('--type', type=str, default='html')
argparser.add_argument('--from_lang', type=str, default='en')
argparser.add_argument('--to_lang', type=str, default='zh-CN')
argparser.add_argument('--min_font', type=int, default=None)
argparser.add_argument('--max_font', type=int, default=None)
argparser.add_argument('--translate', type=bool, default=True)
args = argparser.parse_args()

src_path = args.src
out_path = args.out
out_type = args.type
from_lang = args.from_lang
to_lang = args.to_lang
translated = args.translate

terminal = Terminal(out_path)


def call_terminal():
    terminal.finish_translated()


if src_path is None or out_path is None:
    terminal.show_error('--src 以及 --out 参数不得为空！')
    sys.exit(1)

if from_lang not in Supported_languages or to_lang not in Supported_languages or \
                from_lang == to_lang:
    translated = False
    terminal.show_warning('不合法的输入与输出语言，程序将禁用翻译功能。')
    sys.exit(1)

text_filter = line_height_partial(max=args.max_font, min=args.min_font)

try:
    parser = Parser(src_path)
    pages = parser.get_pages()

    if out_type == 'html':
        printer = Printer(out_path, title=parser.get_title(), type='html')
    elif out_type == 'txt':
        printer = Printer(out_path, title=parser.get_title(), type='txt')
    else:
        terminal.show_error('不支持的目标类型！')
        sys.exit(1)

    if translated is True:
        translator = Translator()

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

        if translated is True:
            translator.translate_layout(parsed_layout, from_lang, to_lang, call_terminal)
        if out_type == 'html':
            printer.print_html_page(parsed_layout, text_filter=text_filter)
        elif out_type == 'txt':
            printer.print_txt_page(parsed_layout)
        count += 1
        if count >= 1:
            break
    printer.save()
except Exception as e:
    terminal.show_error(repr(e))
    sys.exit(1)

terminal.show_end()


# TODO: 针对于具体错误进行处理
# TODO: 补全对于jpeg image 的处理
# TODO: 纯文本处理
# TODO: 打包成 exe
# TODO: 去除 pdfminer 的 warning
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
