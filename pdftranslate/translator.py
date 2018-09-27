import re
import urllib
from urllib import request
import js2py
import json

from pdftranslate.parser import ParsedTextBox

Index_url = r'https://translate.google.cn/'
Base_url = r'https://translate.google.cn/translate_a/single'
Supported_languages = ['en', 'zh-CN', 'ja']

# 后续 TK 的计算方式可能还会改变，所以只能用着持续跟进了
# 之前版本的 TKK 计算方式，现在已经被船新版本替代了
# # TKK=eval('((function(){var a\x3d1101234144;var b\x3d-234397642;return 426728+\x27.\x27+(a+b)})())');
# Reg_tkk = "TKK=eval\(\'\(\(function\(\){var a\\\\x3d(-?[0-9]*);var b\\\\x3d(-?[0-9]*);return (-?[0-9]*)\+\\\\x27.\\\\x27\+\(a\+b\)}\)\(\)\)\'\);"
#
#
# def calc_tkk(ret):
#     regs = ret.regs
#     # print("TKK=eval('((function(){var a\\x3d" + ret.string[regs[1][0]:regs[1][1]] +
#     #       ";var b\\x3d" + ret.string[regs[2][0]:regs[2][1]] +
#     #       ";return " + ret.string[regs[3][0]:regs[3][1]] + "+\\x27.\\x27+(a+b)})())');")
#
#     a = int(ret.string[regs[1][0]:regs[1][1]])
#     b = int(ret.string[regs[2][0]:regs[2][1]])
#     c = int(ret.string[regs[3][0]:regs[3][1]])
#     temp = a + b
#     return str(c) + '.' + str(temp)

Reg_tkk = "TKK=\'(-?[0-9]*).(-?[0-9]*)\';"


def calc_tkk(ret):
    regs = ret.regs

    a = int(ret.string[regs[1][0]:regs[1][1]])
    b = int(ret.string[regs[2][0]:regs[2][1]])
    return str(a) + '.' + str(b)


def get_tkk():
    headers = {
        'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
    req = request.Request(url=Index_url, headers=headers)
    response = request.urlopen(req)
    page = response.read()
    page = page.decode('utf-8')

    ret = re.search(Reg_tkk, page)
    return calc_tkk(ret)


get_tk = js2py.eval_js("""
function vq(a,uq) {
  function sq(a) {
    return function() {
      return a
    }
  }
  
  function tq(a, b) {
    for (var c = 0; c < b.length - 2; c += 3) {
      var d = b.charAt(c + 2);
      d = "a" <= d ? d.charCodeAt(0) - 87 : Number(d);
      d = "+" == b.charAt(c + 1) ? a >>> d : a << d;
      a = "+" == b.charAt(c) ? a + d & 4294967295 : a ^ d
    }
    return a
  }

  if (null !== uq)
    var b = uq;
  else {
    b = sq('T');
    var c = sq('K');
    b = [b(), c()];
    b = (uq = window[b.join(c())] || "") || ""
  }
  var d = sq('t');
  c = sq('k');
  d = [d(), c()];
  c = "&" + d.join("") + "=";
  d = b.split(".");
  b = Number(d[0]) || 0;
  for (var e = [], f = 0, g = 0; g < a.length; g++) {
    var l = a.charCodeAt(g);
    128 > l ? e[f++] = l : (2048 > l ? e[f++] = l >> 6 | 192 : (55296 == (l & 64512) && g + 1 < a.length && 56320 == (a.charCodeAt(g + 1) & 64512) ? (l = 65536 + ((l & 1023) << 10) + (a.charCodeAt(++g) & 1023),
      e[f++] = l >> 18 | 240,
      e[f++] = l >> 12 & 63 | 128) : e[f++] = l >> 12 | 224,
      e[f++] = l >> 6 & 63 | 128),
      e[f++] = l & 63 | 128)
  }
  a = b;
  for (f = 0; f < e.length; f++)
    a += e[f],
      a = tq(a, "+-a^+6");
  a = tq(a, "+-3^+b+-f");
  a ^= Number(d[1]) || 0;
  0 > a && (a = (a & 2147483647) + 2147483648);
  a %= 1000000;
  return c + (a.toString() + "." + (a ^ b))
};
""")


class Translator(object):
    def __init__(self):
        self.tkk = get_tkk()
        self.tk = None

    def translate(self, input_text, from_language='en', to_language='zh-CN'):
        if from_language == to_language or \
                        from_language not in Supported_languages or \
                        to_language not in Supported_languages:
            return input_text

        self.tk = get_tk(input_text, self.tkk)

        data = {
            'client': 't',
            'sl': from_language,
            'tl': to_language,
            'hl': to_language,
            'ie': 'UTF-8',
            'oe': 'UTF-8',
            'otf': 1,
            'ssel': 0,
            'tsel': 0,
            'kc': 0
        }
        dt = ['at', 'bd', 'ex', 'ld', 'md', 'qca', 'rw', 'rm', 'ss', 't']
        dt_str = ''
        for dt_item in dt:
            dt_str += '&dt=' + dt_item
        url = Base_url + '?' + urllib.parse.urlencode(data) + dt_str + self.tk

        headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
        payload = {'q': input_text}
        try:
            req = request.Request(url=url, headers=headers, data=urllib.parse.urlencode(payload).encode('utf-8'))
            response = request.urlopen(req)
        except urllib.error.HTTPError as e:
            # print(e.read().decode("utf8"))
            return input_text
        body = json.loads(response.read().decode('utf-8'))
        translated = ''
        for line in body[0]:
            if line[0] is not None:
                translated += line[0]

        return translated

    def translate_layout(self, root, from_language, to_language, callback=None):
        for item in root.children:
            self._translate_item(item, from_language, to_language)
            if callback is not None:
                callback()
        return root

    def _translate_item(self, layout, from_language, to_language):
        if isinstance(layout, ParsedTextBox):
            translated = self.translate(layout.get_raw_text(False), from_language, to_language)
            layout.set_translated(translated)
