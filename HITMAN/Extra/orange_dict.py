class OrangeDict(dict):
    def __init__(self, mapping=None, /, **kwargs):
        if mapping is not None:
            mapping = {
                value: key for key, value in mapping.items()
            }
        else:
            mapping = {}
        if kwargs:
            mapping.update(
                {value: key for key, value in kwargs.items()}
            )
        super().__init__(mapping)

    def __str__(self):
        print('Используется OrangeDict')
        count = 1
        for key, value in self.items():
            print(f'{count}. {key}: {value}')
            count += 1
        return ''
    
    def __get__(self, key):
        if key in self.keys():
            return self[key]
        return 'Уважаемый пользователь, в списке нет ключа, данные по которому вы пытаетесь достать.'
    
    def __values__(self):
        return (tuple(self.keys()))
    
    def __keys__(self):
        return ''.join([str(e) for e in list(self.values())])
    
    def __copy__(self):
        copy_dict = {}
        for key in self.keys():
            copy_dict[str(key)] = None
        return copy_dict
    
    def true_form_of_dict(self, k):
        true_dict = {}
        for i in range(2, k+1):
            for key, value in self.items():
                true_dict[key * i] = value * i
        return true_dict