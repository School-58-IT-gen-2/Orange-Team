from view.player_view import PlayerView


#Класс, описывающий вывод и ввод в консоль
class ConsoleView(PlayerView):

    def response(self, response):
        if response != '':
            print(f'\n\n{response}')

    def request(self):
        request = input('\n')
        return request