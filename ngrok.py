def get_ngrok_domen_name(log_path='/root/ngrok/log.log'):
    """Возвращает последнее доменное имя из лога ngrok'а"""
    with open(log_path, 'r') as log_file:
        log = log_file.read()
    list_found = list(re.finditer(r'addr=http://localhost:8443 url=https://.{1,40}.eu.ngrok.io', log))
    match = list_found[-1].group() if list_found else None
    result = re.sub(r'^addr=http://localhost:8443 url=', '', match)
    print('*'*100)
    print(f'Domen name found: {result}')
    return result
