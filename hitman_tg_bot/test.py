def tg_text_convert(text: str) -> str:
    restricted_symbols = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for i in restricted_symbols:
        text = text.replace(i, '\\' + i)
    return text
    
print('-', '\U00002014','\U00002E3A')