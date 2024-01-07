from model.common.npcs import NPC, Target


#Класс, описывающий NPC в Хоккаидо
class HokkaidoNPCs:
    def __init__(self):
        self.__npcs = {
            'Shoichi Kataoka':
                NPC(True, 'Телохранитель', True, {0: 'Канатная дорога'}, 5, 'Shoichi Kataoka'),
            'Hidaka Uno':
                NPC(True, 'Телохранитель', True, {0: 'Канатная дорога'}, 5, 'Hidaka Uno'),
            'Nikica Pranjić':
                NPC(True, 'Охранник', True, {0: 'Холл'}, 8, 'Nikica Pranjić'),
            'Toshimi Shinden':
                NPC(True, 'Охранник', True, {0: 'Холл'}, 8, 'Toshimi Shinden'),
            'Hans Hansson':
                NPC(True, 'Охранник', True, {0: 'Холл', 1: 'Комната охраны'}, 8, 'Hans Hansson'),
            'Masashi Morioka':
                NPC(True, 'Охранник', True, {0: 'Зона спа'}, 4, 'Masashi Morioka'),
            'Tadao Motsuzuki':
                NPC(True, 'Охранник', True, {0: 'Ресторан'}, 8, 'Tadao Motsuzuki'),
            'Hidetoshi Higa':
                NPC(True, 'Охранник', True, {0: 'Ресторан'}, 9, 'Hidetoshi Higa'),
            'Oliver Drabløs':
                NPC(True, 'Охранник', True, {0: 'Внутренний сад'}, 3, 'Oliver Drabløs'),
            'Yasuaki Inagaki':
                NPC(True, 'Охранник', True, {0: 'Внутренний сад'}, 5, 'Yasuaki Inagaki'),
            'Junya Andou':
                NPC(True, 'Телохранитель', True, {0: 'Мед-комплекс'}, 6, 'Junya Andou'),
            'Homare Kanai':
                NPC(True, 'Телохранитель', True, {0: 'Мед-комплекс'}, 7, 'Homare Kanai'),
            'Toshihisa Taniguchi':
                NPC(True, 'Телохранитель', True, {0: 'Мед-комплекс'}, 6, 'Toshihisa Taniguchi'),
            'Shuusuke Seki':
                NPC(True, 'Телохранитель', True, {0: 'Мед-комплекс', 1: 'Операционная'}, 9, 'Shuusuke Seki'),
            'Kyuuya Sugiyama':
                NPC(True, 'Охранник', True, {0: 'Комната охраны'}, 9, 'Kyuuya Sugiyama'),
            'Max Gerber':
                NPC(True, 'Охранник', True, {0: 'Гараж'}, 7, 'Max Gerber'),
            'John Maverick':
                NPC(True, 'Охранник', True, {0: 'Коридор за барной стойкой'}, 2, 'John Maverick'),
            'Miamoto San':
                NPC(True, 'Телохранитель', True, {0: 'Морг'}, 2, 'Miamoto San'),
            'Kyouta Shinden':
                NPC(True, 'Телохранитель', True, {0: 'Номер Юки Ямадзаки', 1: 'Холл'}, 8, 'Kyouta Shinden'),
            'Hayaki Fukasawa':
                NPC(True, 'Телохранитель', True, {0: 'Номер Юки Ямадзаки', 1: 'Холл'}, 9, 'Hayaki Fukasawa'),
            'Kaimei Kuroki':
                NPC(True, 'Телохранитель', True, {0: 'Номер Юки Ямадзаки'}, 8, 'Kaimei Kuroki'),
            'Kou Tokunaga':
                NPC(True, 'Телохранитель', True, {0: 'Номер Юки Ямадзаки'}, 7, 'Kou Tokunaga'),
            'Salvio Parra Rojo':
                NPC(True, 'Телохранитель', True, {0: 'Номер Юки Ямадзаки'}, 7, 'Salvio Parra Rojo'),
            'Yoshikazu Sasaki':
                NPC(True, 'Телохранитель', True, {0: 'Номер Юки Ямадзаки'}, 7, 'Yoshikazu Sasaki'),
            'Samuel Santos Lima':
                NPC(True, 'Телохранитель', True, {0: 'Вертолетная площадка'}, 8, 'Samuel Santos Lima'),
            'Rafn Helguson':
                NPC(True, 'Телохранитель', True, {0: 'Вертолетная площадка'}, 9, 'Rafn Helguson'),
            'Hayato Shinden':
                NPC(True, 'Телохранитель', True, {0: 'Мед-комплекс (2 этаж)'}, 8, 'Hayato Shinden'),
            'Shuusuke Kitajima':
                NPC(True, 'Телохранитель', True, {0: 'Мед-комплекс (2 этаж)'}, 9, 'Shuusuke Kitajima'),
            'Sorahiko Satou':
                NPC(True, 'Телохранитель', True, {0: 'Мед-комплекс (2 этаж)'}, 7, 'Sorahiko Satou'),
            'Satomu Sugiyama':
                NPC(True, 'Телохранитель', True, {0: 'Мед-комплекс (2 этаж)'}, 8, 'Satomu Sugiyama'),
            'Nokadota':
                NPC(True, 'Телохранитель', True, {0: 'Номер Юки Ямадзаки', 1: 'Холл', 2: 'Ресторан', 3: 'Холл', 4: 'Зона спа', 5: 'Зона отдыха', 6: 'Зона спа', 7: 'Холл', 8: 'Номер Юки Ямадзаки'}, 8, 'Nokadota'),
            'Yuuto Saiki':
                NPC(True, 'Телохранитель', True, {0: 'Номер Юки Ямадзаки', 1: 'Холл', 2: 'Ресторан', 3: 'Холл', 4: 'Зона спа', 5: 'Зона отдыха', 6: 'Зона спа', 7: 'Холл', 8: 'Номер Юки Ямадзаки'}, 8, 'Yuuto Saiki'),
            'Tamika Oomori':
                NPC(False, 'Работник "ГАМА"', True, {0: 'Зона спа', 1: 'Зона отдыха'}, 7, 'Tamika Oomori'),
            'Harumi Sakei':
                NPC(False, 'Работник "ГАМА"', True, {0: 'Зона спа'}, 8, 'Harumi Sakei'),
            'Kouko Yoshioka':
                NPC(False, 'Работник "ГАМА"', True, {0: 'Ресторан'}, 7, 'Kouko Yoshioka'),
            'Risae Oosawa':
                NPC(False, 'Работник "ГАМА"', True, {0: 'Ресторан'}, 8, 'Risae Oosawa'),
            'Maury Veich':
                NPC(False, 'Работник "ГАМА"', True, {0: 'Внутренний сад'}, 1, 'Maury Veich'),
            'Johan Ishibashi':
                NPC(False, 'Работник "ГАМА"', True, {0: 'Внутренний сад'}, 3, 'Johan Ishibashi'),
            'Saita Shinoda':
                NPC(False, 'Хирург', True, {0: 'Мед-комплекс', 1: 'Операционная'}, 9, 'Saita Shinoda'),
            'Tomochika Honma':
                NPC(False, 'Механик', True, {0: 'Гараж'}, 1, 'Tomochika Honma'),
            'J. Brooke':
                NPC(False, 'Инструктор по йоге', True, {0: 'Гараж', 1: 'Спальня персонала'}, 1, 'J. Brooke'),
            'Ikkei Tsutsui':
                NPC(False, 'Шеф', True, {0: 'Кухня'}, 7, 'Ikkei Tsutsui'),
            'Minao Morishita':
                NPC(False, 'Шеф', True, {0: 'Кухня'}, 8, 'Minao Morishita'),
            'Katshi Ito':
                NPC(False, 'Работник морга', True, {0: 'Морг'}, 6, 'Katshi Ito'),
            'Tenri Shinosaki':
                NPC(False, 'Работник морга', True, {0: 'Морг'}, 7, 'Tenri Shinosaki'),
            'Shoudai Kurosawa':
                NPC(False, 'Работник морга', True, {0: 'Морг'}, 5, 'Shoudai Kurosawa'),
            'Kii Ine':
                NPC(False, 'Хирург', True, {0: 'Операционная'}, 7, 'Kii Ine'),
            'Emiri Nimiya':
                NPC(False, 'Хирург', True, {0: 'Операционная'}, 9, 'Emiri Nimiya'),
            'Gakushi Yamaoka':
                NPC(False, 'Хирург', True, {0: 'Операционная'}, 8, 'Gakushi Yamaoka'),
            'Nicholas Laurent':
                NPC(False, 'Главный хирург', True, {0: 'Операционная'}, 7, 'Nicholas Laurent'),
            'Nails':
                NPC(False, 'Пилот', True, {0: 'Комната пилота', 1: 'Вертолетная площадка', 2: 'Комната пилота', 3: 'Комната пилота'}, 3, 'Nails'),
            'Akira Nakamura':
                NPC(False, 'Директор клиники', True, {0: 'Холл', 1: 'Внутренний сад', 2: 'Холл', 3: 'Мед-комплекс', 4: 'Мед-комплекс (2 этаж)', 5: 'Комната директора клиники', 6: 'Комната директора клиники', 7:'Комната директора клиники', 8: 'Мед-комплекс (2 этаж)', 9: 'Мед-комплекс', 10: 'Холл'}, 7, 'Akira Nakamura')
        }

    def get_by_name(self, name):
        return self.__npcs[name]

    def get_all(self):
        return self.__npcs.values()
    
class HokkaidoTargets:

    def __init__(self):
        self.__targets = {
            'Юки Ямадзаки':
                Target(
                    True, 
                    {
                        0: 'Номер Юки Ямадзаки',
                        1: 'Холл',
                        2: 'Ресторан',
                        3: 'Холл',
                        4: 'Зона спа',
                        5: 'Зона отдыха',
                        6: 'Зона спа',
                        7: 'Холл',
                        8: 'Номер Юки Ямадзаки'
                    },
                    'Юки Ямадзаки'
                    ),
            'Эрих Содерс':
                Target(
                    True,
                    {
                        0: 'Операционная'
                    },
                    'Эрих Содерс'
                )
        }
    
    def get_by_name(self, name):
        return self.__targets[name]

    def get_all(self):
        return list(self.__targets.values())