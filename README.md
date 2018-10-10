# pdf-translate
A simple tool to translate text in pdf file.

## Introduction
Basically, pdf-translate will parse the texts from pdf file and output to html/txt file after translation is completed.
Pdf-translate will **keep the layout of pdf file unchanged** and **provide a comparison of the original text**,
so it will be easy to read the output file.


~~Well, if you just like to output to txt file, I can't make sure that you could get the correct paragraph order.~~


## Usage
For now, you can try the pre-release version of pdf-translate.
It still takes time to improve, but it works fine on simple pdf files.

A simple command of using pdf-translate is:
`.\pdf-translate.exe --src=.\test.pdf --out=.\output.html`

A complex one is: 
`.\pdf-translate.exe --src=.\test.pdf --out=.\output.html --type=html --from_lang=en --to_lang=zh-CN --translate --page=1`

Parameter|Usage|Value|Default
---|-----|---|--
src|the source of pdf file|String|*Required*
out|the path of output file|String|*Required*
type|the output type of file|html/txt|html
from_lang|the origin language|see table below|en
to_lang|the target language|see table below|zh-CN
translate|flag of translating the text|None|True
no-translate|flag of not translating the text|None|True
page|the number of page which need to be operated|[begin,end]/Int|all pages
min_font|the min font size of text which will show|Int|None
max_font|the max font size of text which will show|Int|None

Supported languages is shown as below:

Language|Input
--|--
Simplified Chinese|zh-CN
English|en
Japanese|ja
German|de
Russian|ru
French|fr



## TODOs
- Add hints of parameters.
- Parse and show the images from pdf.
- Remove the warnings from pdfminer.
- Handle complex styles of text including spinning, color and so on.
- Hanlde the special characters like mathematical marks.
- Boxes of text might cover others because the text line of the box may not begin at the left border.
- and so on.


## Warning
- Pdf-translate uses Google translate's api, so it needs to be updated once Google changes its way to generate token.
- Before use the pdf-translate, you need to make sure that your computer has access to [Google translate](https://translate.google.cn/),
and it might work slow because of the http connection.
- It works terrible on the special characters like mathematical marks, for now I just remove all of them. 
So it might looks weird on formulas.
