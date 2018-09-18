import sys
import time


class Terminal(object):
    def __init__(self, path, dest='html', max_steps=50):
        self.max_steps = max_steps
        self.page_count = 0
        self.dest = dest
        self.path = path

        self.curr_page = 0
        self.curr_translated = 0
        self.translated_count = 0

    def set_page_count(self, page_count):
        self.page_count = page_count

    def show_begin(self):
        dest_str = 'HTML'
        if self.dest == 'txt':
            dest_str = 'TXT'
        print('准备将 PDF 转换至 ' + dest_str + ' ，共 ' + str(self.page_count) + '页。')
        return

    # 默认逐页处理，所以 page 只能自增，不能指定
    def begin_page(self, next_total_translated):
        if self.curr_page != 0:
            self.show_process(True)

        self.curr_page += 1
        self.translated_count = next_total_translated
        self.curr_translated = 0
        print('正在处理 page：' + str(self.curr_page) + '/' + str(self.page_count))
        self.show_process()

    def finish_translated(self):
        self.curr_translated += 1
        self.show_process()

    def show_process(self, done=False):
        num_arrow = int(self.curr_translated * self.max_steps / self.translated_count)
        num_line = self.max_steps - num_arrow
        percent = self.curr_translated * 100.0 / self.translated_count
        process_bar = '翻译中：[' + '>' * num_arrow + '-' * num_line + ']' + \
                      '%.2f' % percent + '% ' + \
                      '' + str(self.curr_translated) + '/' + str(self.translated_count) + '\r'
        if done is False:
            sys.stdout.write(process_bar)
            sys.stdout.flush()
        else:
            print(process_bar)
            print('')

    def show_end(self):
        self.show_process(True)
        print('处理完毕，结果输出到：' + self.path)

    def show_warning(self, warning_str=None):
        if warning_str is None:
            print('\nWarning: 未知警告')
        else:
            print('\nWarning: ' + warning_str)
        return

    def show_error(self, error_str=None):
        if error_str is None:
            print('\nError: 出现未知错误，程序终止。')
        else:
            print('\nError: ' + error_str + '\n程序终止。')
        return


# terminal = Terminal(2, 'test')
# terminal.show_begin()
#
# translated = 10
# terminal.begin_page(translated)
#
# terminal.finish_translated()
# # for i in range(translated):
# #     terminal.finish_translated()
# #     time.sleep(0.1)
#
# terminal.show_error()
# # terminal.show_end()
