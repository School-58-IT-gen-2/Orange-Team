from View.player_view import PlayerView


class ConsoleView(PlayerView):

    def response(self, response):
        print(f'\n\n{response}')

    def request(self):
        request = input()
        return request