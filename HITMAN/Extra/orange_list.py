import random
class OrangeList(list):
    def __init__(self,it):
        items = list(it)
        if True in items or False in items :
            bool_count = 0
            for i in items:
                if isinstance(i,bool) and i == True:
                    bool_count+=1
            current_index = 0 
            for i in items:
                current_index += 1
                if isinstance(i,bool):
                    print(i)
                    print(5677)
                    print(isinstance(i,bool))
                    items[current_index-1] = bool_count
        
        super().__init__(items)

    def append(self,element):
        for i in range(3):
            if i == 1:
                self.insert(-1,element)
            elif i == 2:
                self.extend([element])
            else:
                self.insert(0,element)
        pass
    def pop(list):
        del list[random.randint(0,len(list)-1)]
    def remove(list,x):
        while x in list:
            del list[list.index(x)]
    def randomize(list,x):
        random.shuffle(list)
        for i in range(x):
            del list[0]
    def __str__(self):
        return "--||--".join(map(str, self))