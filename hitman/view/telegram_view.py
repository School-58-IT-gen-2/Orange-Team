from view.player_view import PlayerView


class TelegramView(PlayerView):
    
    updater = ''
    context = 1

    def response(self, response, updater: updater, context: context):
        #Отправляет response (строку) пользователю
        pass

    def request(self, button_num, updater: updater, context: context):
        for i in range(button_num):
            #Создает button_num кнопок, на которых номера от 1 до button_num + 1
            #Кнопки возвращают 1 значение -- их номер (пятая кнопка возвращает 5)
            pass