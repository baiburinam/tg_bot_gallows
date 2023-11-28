import random

import telebot

from src.class_game import Game
from src.my_token import token
from src.utils import *

all_words = open_txt(os.path.join('src', 'bank_of_words.txt'))

all_users = {}

results = make_results()

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def start_bot(message):
    bot.send_message(message.from_user.id, f"{message.from_user.first_name}, привет!\nЯ телеграм-бот, "
                                           f"с которым можно поиграть в виселицу.\nЧтобы начать игру, пишите /game. "
                                           f"Если появились трудности, пишите /help.")


@bot.message_handler(commands=['help'])
def help_bot(message):
    bot.send_message(message.from_user.id, f"{message.from_user.first_name}, привет!\nЯ телеграм-бот, "
                                           f"с которым можно поиграть в виселицу.\nЧтобы начать игру, пишите /game.\n"
                                           "Чтобы посмотреть результаты своих игр, пиши /result\n"
                                           "Чтобы посмотреть рейтинг всех игроков, пиши /rating\n"
                                           "\nПравила игры:\n"
                                           "Бот загадывает слово. Вам будет известно количество букв в загаданном "
                                           "слове.\n"
                                           "Далее в каждом сообщении вы можете писать букву, которая, как вам кажется, "
                                           "может быть в загаданном слове. После каждой попытки бот скажет вам, "
                                           "правильно или неправильно угадана буква.\n"
                                           "Будьте внимательны: буква 'е' и буква 'ё' - разные буквы.\n"
                                           "Ваша задача - отгадать слово за 8 попыток, пока человечек не будет "
                                           "подвешен.")


@bot.message_handler(commands=['game'])
def play_bot(message):
    game = Game()

    if all_users.get(message.from_user.id) is None:
        all_users.update({message.from_user.id: game})
    else:
        all_users[message.from_user.id] = game

    print(all_users.keys())

    game.key_word = random.choice(all_words)
    game.hide_word = "*" * len(game.key_word)
    bot.send_message(message.from_user.id,
                     f"Я загадала слово из {len(game.key_word)} букв.\nВот оно: {game.hide_word}.\nВаша "
                     f"задача: угадать все буквы, совершив не более 8 ошибок.\nУдачи!")


@bot.message_handler(commands=['group'])
def group_bot(message):
    bot.send_message(message.from_user.id, 'look for a gamer')


@bot.message_handler(commands=['result'])
def show_result(message):
    cur_id = message.from_user.id

    if not (id_check(str(cur_id), results)):
        bot.send_message(cur_id, "Вы еще ни разу не играли со мной. Хотите попробовать?\nТогда пишите \game.")
    else:
        bot.send_message(cur_id, f"Вы выиграли {results[str(cur_id)].win} игр из {results[str(cur_id)].game}.\n")


@bot.message_handler(commands=['rating'])
def show_rating(message):
    text_rating = ""

    sorted_dict = sorted(results.items(), key=lambda x: x[1].win, reverse=True)
    place = 1

    for item in sorted_dict:
        text_rating += str(place) + '.' + ' ' + item[1].name + ' ' + str(item[1].win) + ' ' + str(item[1].game) + '\n'
        place += 1
        print(item[0], item[1].name, item[1].win, item[1].game)

    bot.send_message(message.from_user.id, "Таблица результатов:\n Имя Победы Игры\n" + text_rating)


@bot.message_handler(content_types=['text'])
def play_game(message):
    cur_id = message.from_user.id

    text = message.text

    if len(text) != 1:
        bot.send_message(cur_id, "Пожалуйста, введите только одну строчную букву.")
    elif not ('а' <= text <= 'я'):
        bot.send_message(cur_id, "Пожалуйста, введите только строчную одну букву от а до я.")
    elif all_users[cur_id].letters.count(text) != 0:
        bot.send_message(cur_id, f"Вы уже вводили эту букву. Попробуйте что-нибудь другое. "
                                 f"Вы вводили буквы: {all_users[cur_id].letters}")
    elif all_users[cur_id].key_word.count(text) != 0:
        for i in range(0, len(all_users[cur_id].key_word)):
            if all_users[cur_id].key_word[i] == text:
                all_users[cur_id].hide_word = all_users[cur_id].hide_word[:i] + text + all_users[cur_id].hide_word[
                                                                                       i + 1:]

        all_users[cur_id].letters.append(text)
        if all_users[cur_id].hide_word.count('*') == 0:
            cur_name = cur_name_define(message.from_user.first_name, message.from_user.last_name)

            end_game(cur_id, cur_name, True, results)

            bot.send_message(cur_id, f"Поздравляю! Вы отгадали слово '{all_users[cur_id].hide_word}'.\n"
                                     f"Чтобы начать снова, пишите /game.\n"
                                     f"Вы выиграли {results[str(cur_id)].win} игр из {results[str(cur_id)].game}.\n"
                                     f"Буду ждать вас на новой игре!")
        else:
            bot.send_message(cur_id, f"Так держать! Вы отгадали букву {text}."
                                     f"\nЗагаданное слово: {all_users[cur_id].hide_word}.\n"
                                     f"Вы уже вводили буквы: {all_users[cur_id].letters}")
    else:
        all_users[cur_id].letters.append(text)
        all_users[cur_id].try_count -= 1

        if all_users[cur_id].try_count != 0:
            spell = right_spell(all_users[cur_id].try_count)

            bot.send_message(cur_id, f"Такой буквы в {all_users[cur_id].hide_word} нет. У вас осталось "
                                     f"{all_users[cur_id].try_count} {spell}. Вы уже вводили буквы: "
                                     f"{all_users[cur_id].letters}")
        else:
            cur_name = cur_name_define(message.from_user.first_name, message.from_user.last_name)

            end_game(cur_id, cur_name, False, results)

            bot.send_message(cur_id, f"Такой буквы в {all_users[cur_id].hide_word} нет. У вас закончились попытки."
                                     f"\nЗагаданное слово: {all_users[cur_id].key_word}.\n"
                                     f"Вы выиграли {results[str(cur_id)].win} игр из {results[str(cur_id)].game}.\n"
                                     f"Чтобы начать снова, пишите /game.\n"
                                     f"Буду рада снова поиграть с вами!")


bot.polling(none_stop=True, interval=0)

