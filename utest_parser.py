import unittest
import parser


class ParserTest(unittest.TestCase):

    def test_resolve_print_text(self):
        self.assertEqual(parser.resolve_print_text('ok'), ' успешно отправлено ')
        self.assertEqual(parser.resolve_print_text('unknown'), ' не отправлено из-за ошибок ')
        self.assertEqual(parser.resolve_print_text('returned to sender'), ' возвращено отправителю ')

    def test_get_from_adress_from_line(self):
        self.assertEqual(parser.get_from_adress_from_line(
            'Jul 10 10:35:54 srv24-s-st postfix/qmgr[3043]: DEEA5DF03F0: from=<info@auraltc.ru>, status=expired, '
            'returned to sender'),
            'info@auraltc.ru')

    def test_get_id_from_line(self):
        self.assertEqual(parser.get_id_from_line(
            'Jul 10 10:35:54 srv24-s-st postfix/qmgr[3043]: DEEA5DF03F0: from=<info@auraltc.ru>, status=expired, '
            'returned to sender'),
            'DEEA5DF03F0')

    def test_pretty_print(self):
        dict_o = {
            ('krasteplokomplekt@yandex.ru', 'ok'): 596,
            ('root@govconsult.ru', 'ok'): 441,
            ('tduds@wmess.ru', 'ok'): 414,
            ('office@iprbookshop.ru', 'ok'): 394,
            ('tduds@webmess.ru', 'ok'): 381
        }
        self.assertEqual(parser.pretty_print_counter(dict_o),
                         '''С адреса: krasteplokomplekt@yandex.ru успешно отправлено 596 сообщений.
С адреса: office@iprbookshop.ru успешно отправлено 394 сообщений.
С адреса: root@govconsult.ru успешно отправлено 441 сообщений.
С адреса: tduds@webmess.ru успешно отправлено 381 сообщений.
С адреса: tduds@wmess.ru успешно отправлено 414 сообщений.''')


if __name__ == '__main__':
    unittest.main()
