import re
import collections
import unittest

def parse():
	f = open('maillog')
	i = 0
	message_ids = {}
	messages_final = []
	for l in f:
		# Получаем ID письма при начале SMTP сессии и
		# сохраняем полученные ID
		if 'sasl_method=LOGIN' in l and 'sasl_username' in l:
			message_ids[get_id_from_line(l)] = { 'from': '', 'status': 'unknown' } # статус сообщения по умолчанию - неизвестен
		elif 'from=' in l and get_id_from_line(l) in message_ids:
			message_ids[get_id_from_line(l)]['from'] = get_from_adress_from_line(l)

		# Если обработаны все заголовки TO, письмо удаляется из списка
		# занятых ID (запись в логе <ID>: removed). 
		if 'removed' in l:
			try:
				message_ids[(get_id_from_line(l))]['status'] = 'ok'
				if message_ids[(get_id_from_line(l))]['from'].strip() != '':
					messages_final.append((message_ids[(get_id_from_line(l))]['from'],message_ids[(get_id_from_line(l))]['status']))
				del message_ids[(get_id_from_line(l))]
			except KeyError:
				# сообщение с данным ключом ещё не попало в список проверяемых сообщений
				# однако уже получает статус removed. Возможно открытие SMTP не попало в фрагмент лога
				pass 
			except:
				print('Unknown error!')
		# Если письмо так и не было отправлено получателю но было возвращено пользователю, то заносим его
		# в список писем как завершённое с ошибкой и со статусом обработки 'returned to sender'
		if 'returned to sender' in l:
			try: 
				message_ids[(get_id_from_line(l))]['status'] = 'returned to sender'
				if message_ids[(get_id_from_line(l))]['from'].strip() != '':
					messages_final.append((message_ids[(get_id_from_line(l))]['from'],message_ids[(get_id_from_line(l))]['status']))
				del message_ids[(get_id_from_line(l))]
			except KeyError:
				# сообщение с данным ключом ещё не попало в список проверяемых сообщений
				# Возможно открытие SMTP не попало в фрагмент лога
				# Сохраняем ифнормацию о таких сообщениях со статусом 'returned to sender'
				ad = get_from_adress_from_line(l)
				if ad.strip() != '':
					messages_final.append((ad,'returned to sender'))
			except:
				print('Unknown error!')

	f.close()
	# Письма, которые не получили статусы 'removed' или 'returned to sender'
	# так же считаем ошибочными, оставляя статус обработки 'unknown'
	for m in message_ids:
		if message_ids[m]['from'].strip() != '':	
			messages_final.append((message_ids[m]['from'],message_ids[m]['status']))
		del m
	# print(messages_final)
	counter=collections.Counter(messages_final)
	print(pretty_print_counter(counter))


def get_id_from_line(line):
	return line[line.index(': ') + 2:].strip().split(':')[0]

def get_from_adress_from_line(line):
	p = re.compile("(?<=from=<).*?(?=>)")
	result = p.search(line)
	return result.group() 

def pretty_print_counter(counter):
	print(counter)
	listOfTuples = []
	prettyString = ''
	for message in counter:
		listOfTuples.append(('С адреса: ' + message[0], resolve_print_text(message[1]) + str(counter[message]) + ' сообщений.'))
	sorted_adress_list = sorted(listOfTuples, key=lambda x: x[0])
	for m in sorted_adress_list:
		prettyString += (m[0] + m[1]) + '\n'
	return prettyString.strip()

def resolve_print_text(text):
	if text == 'ok':
		return ' успешно отправлено '
	if text == 'unknown':
		return ' не отправлено из-за ошибок '
	if text == 'returned to sender':
		return ' возвращено отправителю '

if __name__ == "__main__":
	# unittest.main()
	parse()
