import collections
import re

STATUS_UNKNOWN = 'unknown'
STATUS_OK = 'ok'
STATUS_RETURNED_TO_SENDER = 'returned to sender'


def parse():
    file = open('maillog')
    message_ids = {}
    messages_final = []
    for line in file:
        # Получаем ID письма при начале SMTP сессии и
        # сохраняем полученные ID
        message_id = get_id_from_line(line)
        if 'sasl_method=LOGIN' in line and 'sasl_username' in line:
            message_ids[message_id] = {'from': '', 'status': STATUS_UNKNOWN}  # статус сообщения по умолчанию неизвестен
        elif 'from=' in line and message_id in message_ids:
            message_ids[message_id]['from'] = get_from_adress_from_line(line)

        # Если обработаны все заголовки TO, письмо удаляется из списка
        # занятых ID (запись в логе <ID>: removed). 
        if 'removed' in line:
            try:
                message = message_ids[message_id]
                message['status'] = STATUS_OK
                if message['from'].strip() != '':
                    messages_final.append(
                        (message['from'], message['status']))
                del message_ids[message_id]
            except KeyError:
                # сообщение с данным ключом ещё не попало в список проверяемых сообщений
                # однако уже получает статус removed. Возможно открытие SMTP не попало в фрагмент лога
                pass
            except:
                print('Unknown error!')
        # Если письмо так и не было отправлено получателю но было возвращено пользователю, то заносим его
        # в список писем как завершённое с ошибкой и со статусом обработки STATUS_RETURNED_TO_SENDER
        if STATUS_RETURNED_TO_SENDER in line:
            try:
                message = message_ids[message_id]
                message['status'] = STATUS_RETURNED_TO_SENDER
                if message['from'].strip() != '':
                    messages_final.append(
                        (message['from'], message['status']))
                del message_ids[message_id]
            except KeyError:
                # сообщение с данным ключом ещё не попало в список проверяемых сообщений
                # Возможно открытие SMTP не попало в фрагмент лога
                # Сохраняем ифнормацию о таких сообщениях со статусом STATUS_RETURNED_TO_SENDER
                address = get_from_adress_from_line(line)
                if address.strip() != '':
                    messages_final.append((address, STATUS_RETURNED_TO_SENDER))
            except:
                print('Unknown error!')

    file.close()
    # Письма, которые не получили статусы 'removed' или STATUS_RETURNED_TO_SENDER
    # так же считаем ошибочными, оставляя статус обработки STATUS_UNKNOWN
    for m_id in message_ids:
        message = message_ids[m_id]
        if message['from'].strip() != '':
            messages_final.append((message['from'], message['status']))
    counter = collections.Counter(messages_final)
    print(pretty_print_counter(counter))


def get_id_from_line(line):
    return line[line.index(': ') + 2:].strip().split(':')[0]


def get_from_adress_from_line(line):
    pattern = re.compile("(?<=from=<).*?(?=>)")
    result = pattern.search(line)
    return result.group()


def pretty_print_counter(counter):
    print(counter)
    list_of_tuples = []
    pretty_string = ''
    for message in counter:
        list_of_tuples.append(
            ('С адреса: ' + message[0], resolve_print_text(message[1]) + str(counter[message]) + ' сообщений.'))
    sorted_adress_list = sorted(list_of_tuples, key=lambda x: x[0])
    for mail in sorted_adress_list:
        pretty_string += (mail[0] + mail[1]) + '\n'
    return pretty_string.strip()


def resolve_print_text(text):
    if text == STATUS_OK:
        return ' успешно отправлено '
    if text == STATUS_UNKNOWN:
        return ' не отправлено из-за ошибок '
    if text == STATUS_RETURNED_TO_SENDER:
        return ' возвращено отправителю '


if __name__ == "__main__":
    # unittest.main()
    parse()
