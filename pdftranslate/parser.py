from collections import Iterable
from binascii import b2a_hex
import re

from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice

from pdfminer.layout import LAParams, \
    LTTextBox, LTTextBoxHorizontal, LTTextBoxVertical, \
    LTTextLine, LTTextLineHorizontal, LTTextLineVertical, \
    LTFigure, LTImage, \
    LTChar
from pdfminer.converter import PDFPageAggregator


imageCacheCount = 0


class ParsedRoot(object):
    def __init__(self, item):
        self.item = item
        self._width = item.width
        self._height = item.height
        self.children = []

    def append_child(self, item):
        self.children.append(item)

    def get_width(self, ratio=1):
        return self._width * ratio

    def get_height(self, ratio=1):
        return self._height * ratio

    def get_child_count(self):
        return len(self.children)

    def get_translated_count(self):
        count = 0
        for child in self.children:
            if isinstance(child, ParsedTextBox):
                count += 1
        return count


class ParsedObject(object):
    def __init__(self, item):
        self.item = item
        self._width = item.width
        self._height = item.height
        self._x0 = item.x0
        self._y0 = item.y0
        self._x1 = item.x1
        self._y1 = item.y1

    def get_width(self, ratio=1):
        return self._width * ratio

    def get_height(self, ratio=1):
        return self._height * ratio

    def get_box(self, ratio=1):
        return {
            'x0': self._x0 * ratio,
            'x1': self._x1 * ratio,
            'y0': self._y0 * ratio,
            'y1': self._y1 * ratio,
        }


class ParsedImage(ParsedObject):
    def __init__(self, item):
        ParsedObject.__init__(self, item)
        self.file_name = None
        self.file_path = None
        self.save_image()

    def get_style(self, ratio=1):
        style = {
            'x0': self._x0 * ratio,
            'x1': self._x1 * ratio,
            'y0': self._y0 * ratio,
            'y1': self._y1 * ratio,
            'width': self._width * ratio,
            'height': self._height * ratio,
            'src': self.file_path
        }
        return style

    def save_image(self):
        result = None
        # file_stream = self.item.stream.get_rawdata()
        # if file_stream:
        #     file_ext = self._determine_image_type(file_stream[0:4])
        #     if file_ext:
        #         self.file_name = ''.join([self.item.name, imageCacheCount, file_ext])
        #         self.file_path = ''.join('./temp/', self.file_name)
        #         imageCacheCount += 1
        #
        #         try:
        #             file_obj = open(self.file_path, 'wb')
        #             file_obj.write(file_stream)
        #             file_obj.close()
        #             result = self.file_path
        #         except IOError:
        #             pass
        return result

    def get_image_path(self):
        return self.file_path

    def _determine_image_type(self, stream_first_4_bytes):
        """Find out the image file type based on the magic number comparison of the first 4 (or 2) bytes"""
        file_type = None
        bytes_as_hex = b2a_hex(stream_first_4_bytes)
        if bytes_as_hex.startswith(b'ffd8'):
            file_type = '.jpeg'
        elif bytes_as_hex == b'89504e47':
            file_type = '.png'
        elif bytes_as_hex == b'47494638':
            file_type = '.gif'
        elif bytes_as_hex.startswith(b'424d'):
            file_type = '.bmp'
        return file_type


class ParsedTextBox(ParsedObject):
    def __init__(self, item):
        ParsedObject.__init__(self, item)
        self._translated = None

    def set_translated(self, translated):
        self._translated = translated

    def get_text(self, escape=True):
        if self._translated is not None:
            if escape is True:
                return self._translated.replace('<', '&lt;').replace('>', '&gt;')
            return self._translated
        else:
            return self.get_raw_text(escape)

    def get_raw_text(self, escape=True):
        # 需要去除文字中的连字符以及 (cid:\d+) 所标识的特殊字符
        text = self.item.get_text().replace('-\n', '')
        text = text.replace('\n', ' ')
        if escape is True:
            text = text.replace('<', '&lt;').replace('>', '&gt;')
        return re.sub('\(cid:\d+\)', '?', text)

    def get_style(self, ratio=1):
        line_style = self._get_first_line_style(ratio)
        if line_style is None:
            return

        style = dict({
            'x0': self._x0 * ratio,
            'x1': self._x1 * ratio,
            'y0': self._y0 * ratio,
            'y1': self._y1 * ratio,
            'width': self._width * ratio,
            'height': self._height * ratio,
            'dir': 'horizontal'
        })
        if isinstance(self.item, LTTextBoxVertical):
            style['dir'] = 'vertical'
        return dict(style, **line_style)

    def _get_first_line_style(self, ratio=1):
        line = self._find_first_line()
        if line is None:
            return

        style = {
            'lineHeight': line.median_charheight * ratio
        }
        return style

    def _find_first_line(self):
        for line in self.item:
            if isinstance(line, LTTextLine):
                return line


def parse_item(item, root):
    if isinstance(item, LTTextBox):
        root.append_child(ParsedTextBox(item))
    elif isinstance(item, LTImage):
        root.append_child(ParsedImage(item))
    else:
        if isinstance(item, Iterable):
            for child_item in item:
                parse_item(child_item, root)

    return


def parse_layout(layout):
    root = ParsedRoot(layout)
    for item in layout:
        parse_item(item, root)
    return root


class Parser(object):
    def __init__(self, path, password=''):
        self.path = path
        self.fp = open(path, 'rb')
        self.parser = PDFParser(self.fp)
        self.doc = PDFDocument()
        self.parser.set_document(self.doc)
        self.doc.set_parser(self.parser)
        self.doc.initialize(password)

        self.rsrcmgr = PDFResourceManager()
        self.laparams = LAParams()
        self.device = PDFPageAggregator(self.rsrcmgr, laparams=self.laparams)
        self.interpreter = PDFPageInterpreter(self.rsrcmgr, self.device)

    def get_page_count(self):
        return self.doc.get_pages()

    def get_pages(self):
        return self.doc.get_pages()

    def get_info(self):
        return self.doc.info

    def get_title(self):
        if self.doc.info is not None and len(self.doc.info) > 0:
            if hasattr(self.doc.info[0], 'Title'):
                return self.doc.info[0]['Title']
            else:
                return self.path

    def parse_page(self, page):
        self.interpreter.process_page(page)
        layout = self.device.get_result()
        return parse_layout(layout)
