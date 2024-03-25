#Класс, описывающий вывод и ввод в консоль
class ConsoleView():

    def response(self, response):
        if response != '':
            print(f'\n\n{response}')

    def request(self):
        request = input('\n')
        return request