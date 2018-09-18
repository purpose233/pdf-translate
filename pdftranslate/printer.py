import codecs
import json

from pdftranslate.parser import ParsedTextBox, ParsedImage


Default_margin = 20
Default_ratio = 2


def line_height_partial(min=None, max=None):
    def text_filter(text, style):
        line_height = style['lineHeight']
        if min is not None:
            if line_height < min:
                return False
        if max is not None:
            if line_height > max:
                return False
        return True
    return text_filter


class Printer(object):
    def __init__(self, path, title='', theme='default', type='html', translated=True):
        self.path = path
        self.title = title
        self.theme = theme
        self.type = type
        self.translated = translated

        self.pages = []
        self.count = 0

    def print_txt_page(self, parsed_layout):
        page = []
        for item in parsed_layout.children:
            if isinstance(item, ParsedTextBox):
                text = item.get_text()
                raw_text = item.get_raw_text()

                text_box = dict({
                    'text': text,
                    'raw': raw_text
                })
                page.append(text_box)
        self.pages.append(page)
        return

    def print_txt_all(self, layouts):
        for parsed_layout in layouts:
            self.print_txt_all(parsed_layout)
        return

    def print_html_page(self, parsed_layout, text_filter=None):
        width = parsed_layout.get_width(Default_ratio)
        height = parsed_layout.get_height(Default_ratio)

        page = dict({
            'width': width,
            'height': height,
            'textBoxes': [],
            'images': []
        })

        for item in parsed_layout.children:
            if isinstance(item, ParsedTextBox):
                text = item.get_text()
                raw_text = item.get_raw_text()
                meta_style = item.get_style(Default_ratio)
                if meta_style is None:
                    continue
                if text_filter is not None:
                    if text_filter(text, meta_style) is False:
                        continue
                style = self._generate_style(meta_style, 'text-box', width, height)
                text_box = dict({
                    'text': text,
                    'raw': raw_text,
                    'style': style
                })
                page['textBoxes'].append(text_box)
            elif isinstance(item, ParsedImage):
                meta_style = item.get_style(Default_ratio)
                if meta_style is None:
                    continue
                style = self._generate_style(meta_style, 'image', width, height)
                src = meta_style['src']
                if src is None:
                    src = ''
                image = dict({
                    'src': src,
                    'style': style,
                })
                page['images'].append(image)

        self.pages.append(page)
        self.count += 1

    def print_html_all(self, layouts):
        for parsed_layout in layouts:
            self.print_html_page(parsed_layout)

    def save(self):
        output = ''
        if self.type == 'html':
            style_sheets = self._get_stylesheet()
            template_file = codecs.open('./assets/template.html', "r", 'utf-8')
            # template_file = open('./assets/template.html', 'r')
            template = template_file.read()
            template_file.close()

            template = template.replace('${title}', self.title, 1)
            template = template.replace('${style}', style_sheets, 1)
            template = template.replace('${data}', json.dumps(self.pages), 1)
            output = template
        elif self.type == 'txt':
            output = ''
            page_index = 1
            for page in self.pages:
                output += 'PAGE ' + str(page_index) + ':\n'
                for text_box in page:
                    if self.translated:
                        output += text_box['raw'] + '\n'
                    output += text_box['text'] + '\n'
                output += '\n'
                page_index += 1

        fp = codecs.open(self.path, "w", 'utf-8')
        fp.write(output)
        fp.close()

    def _get_stylesheet(self):
        # 静态资源的获取路径仍是一个问题，也许我应该把所有的静态文件放到内存中
        if self.theme is 'default':
            fp = open('./assets/default.css', 'r')
            style = fp.read()
            fp.close()
            return style
        return ''

    def _generate_style(self, meta_style, item_type, page_width, page_height):
        style = dict({
            'position': 'absolute',
            'left': str(meta_style['x0']) + 'px',
            'top': str(page_height - meta_style['y1']) + 'px',
            'width': str(meta_style['width']) + 'px',
            'height': str(meta_style['height']) + 'px'
        })

        if item_type == 'text-box':
            style['lineHeight'] = str(meta_style['lineHeight']) + 'px'
        # elif item_type == 'image':
        return style


# 不依赖于模板直接生成 html 文件，相比较而言灵活度比较差
class PrinterOld(object):
    def __init__(self, path, title='', theme='default'):
        self.path = path
        self.title = title
        self.theme = theme

        self.pages = []
        self.count = 0
        self.top = Default_margin  # 表示当前 page 的 top offset

    def print_txt_page(self, parsed_layout):
        return

    def print_txt_all(self, layouts):
        return

    def print_html_page(self, parsed_layout, text_filter=None):
        content = ''
        width = parsed_layout.get_width(Default_ratio)
        height = parsed_layout.get_height(Default_ratio)
        for item in parsed_layout.children:
            if isinstance(item, ParsedTextBox):
                text = item.get_text()
                style = item.get_style(Default_ratio)
                if text_filter is not None:
                    if text_filter(text, style) is False:
                        continue
                style_str = self._generate_style(style, 'text-box', width, height)
                pre = '<div class="text-box" style="' + style_str + '">'
                post = '</div>'
                content += pre + text + post
            elif isinstance(item, ParsedImage):
                style = item.get_style(Default_ratio)
                style_str = self._generate_style(style, 'image', width, height)
                src = style['src']
                if src is None:
                    src = ''
                content += '<div class="image" style="' + style_str + '">' \
                           '<img src="' + src + '" alt="Not supported image type.">' \
                           '</div>'

        html = self._complete_page_html(content, width, height)
        self.pages.append(html)
        self.count += 1
        self.top += height + Default_margin

    def print_html_all(self, layouts):
        for parsed_layout in layouts:
            self.print_html_page(parsed_layout)
        return

    def save(self):
        html = self._complete_full_html(self.pages, self.title, self._get_stylesheet())
        # fp = open(self.path, "w")
        # fp.write(html)
        # fp.close()

        fp = codecs.open(self.path, "w", 'utf-8')
        fp.write(html)
        fp.close()

    def _generate_style(self, style, item_type, page_width, page_height):
        style_str = 'position:absolute;'
        style_str += 'left:' + str(style['x0']) + 'px;'
        style_str += 'top:' + str(page_height - style['y1']) + 'px;'
        style_str += 'width:' + str(style['width']) + 'px;'
        style_str += 'height:' + str(style['height']) + 'px;'
        if item_type == 'text-box':
            style_str += 'line-height:' + str(style['lineHeight']) + 'px;'
            # 因为无法获取 font-size 所以用 line-height 比例缩小来模拟
            style_str += 'font-size:' + str(style['lineHeight'] * 0.6) + 'px;'
        elif item_type == 'image':
            style_str += 'background:aliceblue;'
        return style_str

    def _complete_page_html(self, content, width, height):
        top_offset = self.top
        pre = '<div class="page" ' \
              'style="width:' + str(width) + 'px;height:' + str(height) + 'px;' \
              'position:absolute;left:' + str(Default_margin) + 'px;top:' + str(top_offset) + 'px;">'
        post = '</div>'
        return pre + content + post

    def _get_stylesheet(self):
        # 静态资源的获取路径仍是一个问题，也许我应该把所有的静态文件放到内存中
        if self.theme is 'default':
            fp = open('./assets/default.css', 'r')
            style = fp.read()
            fp.close()
            return style
        return ''

    def _complete_full_html(self, contents, title, style):
        pre = '<!DOCTYPE html>' \
              '<html>' \
              '<head>' \
              '<meta charset="UTF-8">' \
              '<title>' + title + '</title>' \
              '<style>' + style + '</style>' \
              '</head>' \
              '<body>'
        post = '</body>' \
               '</html>'
        if isinstance(contents, list):
            full_content = ''
            for content in contents:
                full_content += content
            return pre + full_content + post
        elif isinstance(contents, str):
            return pre + contents + post
