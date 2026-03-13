import codecs

with codecs.open('error.log', 'r', encoding='utf-16le') as f:
    in_tb = False
    for line in f:
        if 'Traceback (' in line:
            in_tb = True
            print('--- TRACEBACK START ---')
        if in_tb:
            print(line, end='')
            if '500 Internal Server Error' in line or 'pydantic_core' in line or 'SQLAlchemyError' in line or 'AttributeError' in line:
                in_tb = False
