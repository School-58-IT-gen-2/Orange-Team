from model.player.player_info import player_lvl


#Класс, описывающий испытания на локации
class Challenge:

    def __init__(self, name, description, completed):
        self.name = name
        self.description = description
        self.completed = completed

    #Уведомление о выполнении условий испытания
    def achieved(self):
        global player_lvl
        if self.completed == False:
            self.completed = True
            player_lvl[0] += 5
            return f'Испытание выполнено: {self.name}'
        return ''
    
    #Вывод описания испытания
    def challenge_info(self):
        result_string = f'{self.name}\n\n{self.description}\n\n1. Назад'
        return(result_string)