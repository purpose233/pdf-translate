import sys
import argparse

from pdftranslate.parser import Parser
from pdftranslate.translator import Translator, Supported_languages
from pdftranslate.printer import Printer, line_height_partial
from pdftranslate.terminal import Terminal

argparser = argparse.ArgumentParser(description='manual to this script')
argparser.add_argument('--src', type=str, default=None, required=True)
argparser.add_argument('--out', type=str, default=None, required=True)
argparser.add_argument('--type', type=str, default='html')
argparser.add_argument('--from_lang', type=str, default='en')
argparser.add_argument('--to_lang', type=str, default='zh-CN')
argparser.add_argument('--min_font', type=int, default=None)
argparser.add_argument('--max_font', type=int, default=None)
# argparser.add_argument('--translate', type=bool, default=True)

translated_parser = argparser.add_mutually_exclusive_group(required=False)
translated_parser.add_argument('--translate', dest='translate', action='store_true')
translated_parser.add_argument('--no-translate', dest='translate', action='store_false')
argparser.set_defaults(translate=True)

argparser.add_argument('--page', type=int, default=None)
args = argparser.parse_args()

src_path = args.src
out_path = args.out
out_type = args.type
from_lang = args.from_lang
to_lang = args.to_lang
translated = args.translate
page_count = args.page

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

if page_count is not None and page_count < 1:
    terminal.show_warning('转换的页数需大于等于1，将默认转换全部内容')
    page_count = None

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

    if page_count is not None:
        terminal.set_page_count(page_count)
    else:
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
        if page_count is not None and count >= page_count:
            break
    printer.save()
except Exception as e:
    terminal.show_error(repr(e))
    sys.exit(1)

terminal.show_end()


# TODO: 处理 bezier 曲线、直线、表格等 pdf 元素
# TODO: page 参数改变，用 [x,y] / count 替代
# TODO: 更多语言支持
# TODO: 特殊字符的处理
# TODO: 补全对于 image 的处理
# TODO: 去除 pdfminer 的 warning
# TODO: 一个 textbox 内部可能有一个复杂的相对位置的结构，同时看起来在同一个 box 内部的文字可能会分在两个部分，导致出现遮挡问题
# TODO: 处理复杂文字样式：竖排文字，可能还有旋转之类的。。。
# TODO: 输出的 html 屏幕适配
# TODO: 输出的 html 中添加一键复制等功能

# 示例输入：python ./main.py --src=./temp/test01.pdf --out=./temp/output.html --type=html --from_lang=en --to_lang=zh-CN --no-translate --page=1
