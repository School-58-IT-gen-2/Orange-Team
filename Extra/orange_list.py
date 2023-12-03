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
                    items[current_index-1] = bool_count
        
        super().__init__(items)

    def append(self,element):
        for i in range(3):
            if i == 1:
                self.insert(random.randint(0,len(self)-1),element)
            elif i == 2:
                self.extend([element])
            else:
                self.insert(0,element)
        pass
    def pop(self):
        x = random.randint(0,len(self)-1)
        y = self[x]
        del self[x]
        return y
    def remove(self,x):
        while x in self:
            del self[self.index(x)]
    def randomize(self,x):
        random.shuffle(list)
        for i in range(x):
            del self[0]
    def __str__(self):
        return "--||--".join(map(str, self))