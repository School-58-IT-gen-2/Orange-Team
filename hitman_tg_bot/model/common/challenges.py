from model.player.player_info import player_lvl


#Класс, описывающий испытания на локации
class Challenge:

    def __init__(self, name, description, completed=False):
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