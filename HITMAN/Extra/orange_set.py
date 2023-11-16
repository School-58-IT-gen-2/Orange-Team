class ArgumentList(list):
     pass

class OrangeSet(list):
    def __init__(self, args):
            if isinstance(args,ArgumentList):
                self.args = args
                temporary_list = []
                for i in range(len(self.args)):
                    temporary_list.append([])
                list_count = 0
                for i in self.args:
                    if i not in temporary_list[list_count]:
                        temporary_list[list_count].append(i)
                    else:
                        list_count += 1
                        temporary_list[list_count].append(i)
                super().__init__(max(temporary_list, key=len))
            else:
                print("Пусть это будет написано на твоей скудной могиле: впишите значение OrangeList")
                return None
