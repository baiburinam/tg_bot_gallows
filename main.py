import random

import telebot

from src.class_game import Game
from src.utils import *

all_words = open_txt(os.path.join('src', 'bank_of_words.txt'))

gallows = open_json(os.path.join('src', 'gallows.json'))

all_users = {}

all_query = {}

results = make_results()

bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))


@bot.message_handler(commands=['start'])
def start_bot(message):
    bot.send_message(message.from_user.id, f"{message.from_user.first_name}, привет!\nЯ телеграм-бот, "
                                           f"с которым можно поиграть в виселицу.\nЧтобы начать игру, пиши /game. "
                                           f"Если появились трудности, пиши /help.")


@bot.message_handler(commands=['help'])
def help_bot(message):
    bot.send_message(message.from_user.id, f"{message.from_user.first_name}, привет!\nЯ телеграм-бот, "
                                           f"с которым можно поиграть в виселицу.\nЧтобы начать игру, пиши /game.\n"
                                           "Чтобы посмотреть результаты своих игр, пиши /result\n"
                                           "Чтобы посмотреть рейтинг всех игроков, пиши /rating\n"
                                           "\nПравила игры:\n"
                                           "Бот загадывает слово. Тебе будет известно количество букв в загаданном "
                                           "слове.\n"
                                           "Далее в каждом сообщении ты можешь писать букву, которая, как тебе кажется,"
                                           " может быть в загаданном слове. После каждой попытки бот скажет тебе, "
                                           "правильно или неправильно угадана буква.\n"
                                           "Будь внимательным игроком: буква 'е' и буква 'ё' - разные буквы.\n"
                                           "Твоя задача - отгадать слово за 8 попыток, пока человечек не будет "
                                           "подвешен.")


@bot.message_handler(commands=['play_with'])
def group_command(message):
    cur_text = ""
    step = 1

    sorted_dict = sorted(results.items(), key=lambda x: x[1].win, reverse=True)

    for item in sorted_dict:
        if item[1].name != cur_name_define(message.from_user.first_name, message.from_user.last_name):
            cur_text += str(step) + '.' + ' ' + item[1].name + '\n'
            step += 1

    if cur_text == "":
        bot.send_message(message.from_user.id, "К сожалению, кроме тебя со мной никто не играл и ты не сможешь "
                                               "загадать другому пользователю слово.")
    else:
        bot.send_message(message.from_user.id, cur_text)
        bot.send_message(message.from_user.id, "Чтобы загадать слово одному из других пользователей, напиши мне "
                                           "следующим сообщением его номер в списке и загаданное тобой слово.\n"
                                           "Например: 1 крокодил.\nПосле игры я напишу тебе ее результат.")


@bot.message_handler(commands=['game'])
def play_bot(message):
    game = Game()

    if all_users.get(message.from_user.id) is None:
        all_users.update({message.from_user.id: game})
    else:
        all_users[message.from_user.id] = game

    all_users[message.from_user.id].game_on = True

    game.key_word = random.choice(all_words)
    game.hide_word = "*" * len(game.key_word)
    bot.send_message(message.from_user.id,
                     f"Я загадала слово из {len(game.key_word)} букв.\nВот оно: {game.hide_word}.\nТвоя "
                     f"задача: угадать все буквы, совершив не более 8 ошибок.\nУдачи!")


@bot.message_handler(commands=['result'])
def show_result(message):
    cur_id = message.from_user.id

    if not (id_check(str(cur_id), results)):
        bot.send_message(cur_id, "Ты еще ни разу не играл(а) со мной. Хочешь попробовать?\nТогда пиши \game.")
    else:
        bot.send_message(cur_id, f"Ты выиграл(а) {results[str(cur_id)].win} игр из {results[str(cur_id)].game}.\n")


@bot.message_handler(commands=['rating'])
def show_rating(message):
    text_rating = ""

    sorted_dict = sorted(results.items(), key=lambda x: x[1].win, reverse=True)
    place = 1

    for item in sorted_dict:
        text_rating += str(place) + '.' + ' ' + item[1].name + ' ' + str(item[1].win) + ' ' + str(item[1].game) + '\n'
        place += 1

    bot.send_message(message.from_user.id, "Таблица результатов:\n Имя Победы Игры\n" + text_rating)


@bot.message_handler(content_types=['text'])
def play_game(message):
    if all_users[message.from_user.id].game_on:
        cur_id = message.from_user.id

        text = message.text

        if len(text) != 1:
            bot.send_message(cur_id, "Пожалуйста, введи только одну строчную букву.")
        elif not ('а' <= text <= 'я'):
            bot.send_message(cur_id, "Пожалуйста, введи только строчную одну букву от а до я.")
        elif all_users[cur_id].letters.count(text) != 0:
            bot.send_message(cur_id, f"Ты уже вводил(а) эту букву. Попробуй что-нибудь другое. "
                                     f"Ты вводил(а) буквы: {all_users[cur_id].letters}")
        elif all_users[cur_id].key_word.count(text) != 0:
            for i in range(0, len(all_users[cur_id].key_word)):
                if all_users[cur_id].key_word[i] == text:
                    all_users[cur_id].hide_word = all_users[cur_id].hide_word[:i] + text + all_users[cur_id].hide_word[
                                                                                           i + 1:]

            all_users[cur_id].letters.append(text)
            if all_users[cur_id].hide_word.count('*') == 0:
                cur_name = cur_name_define(message.from_user.first_name, message.from_user.last_name)

                all_users[cur_id].game_on = False
                end_game(cur_id, cur_name, True, results)

                if all_users[message.from_user.id].group != 0:
                    bot.send_message(all_users[message.from_user.id].group, f"Пользователь {cur_name} отгадал(а) слово"
                                                                            f" {all_users[cur_id].hide_word}!")

                bot.send_message(cur_id, f"Поздравляю! Ты отгадал(а) слово '{all_users[cur_id].hide_word}'.\n"
                                         f"Чтобы начать снова, пиши /game.\n"
                                         f"Ты выиграл(а) {results[str(cur_id)].win} игр из {results[str(cur_id)].game}.\n"
                                         f"Буду ждать тебя на новой игре!")
            else:
                bot.send_message(cur_id, f"Так держать! Ты отгадал(а) букву {text}."
                                         f"\nЗагаданное слово: {all_users[cur_id].hide_word}.\n"
                                         f"Ты уже вводил(а) буквы: {all_users[cur_id].letters}")
        else:
            all_users[cur_id].letters.append(text)
            all_users[cur_id].try_count -= 1

            if all_users[cur_id].try_count != 0:
                spell = right_spell(all_users[cur_id].try_count)
                step = str(8 - all_users[cur_id].try_count)

                bot.send_message(cur_id, f"Такой буквы в {all_users[cur_id].hide_word} нет. У тебя осталось "
                                         f"{all_users[cur_id].try_count} {spell}. Ты уже вводил(а) буквы: "
                                         f"{all_users[cur_id].letters}")
                bot.send_message(cur_id, gallows[step])
            else:
                cur_name = cur_name_define(message.from_user.first_name, message.from_user.last_name)

                all_users[cur_id].game_on = False

                end_game(cur_id, cur_name, False, results)

                if all_users[message.from_user.id].group != 0:
                    bot.send_message(all_users[message.from_user.id].group, f"Пользователь {cur_name} не отгадал(а)"
                                                                            f" слово {all_users[cur_id].hide_word}!")

                bot.send_message(cur_id, f"Такой буквы в {all_users[cur_id].hide_word} нет. У тебя закончились попытки."
                                         f"\nЗагаданное слово: {all_users[cur_id].key_word}.\n"
                                         f"Ты выиграл(а) {results[str(cur_id)].win} игр из {results[str(cur_id)].game}.\n"
                                         f"Чтобы начать снова, пиши /game.\n"
                                         f"Буду рада снова поиграть с тобой!")
                bot.send_message(cur_id, gallows[str(8)])
    else:
        sorted_dict = sorted(results.items(), key=lambda x: x[1].win, reverse=True)
        inf = message.text.split()

        num_player = 0

        if len(inf[0]) == 1 and inf[0].isdigit():
            num_player = int(inf[0])

        if not (1 <= num_player <= len(sorted_dict) - 1):
            bot.send_message(message.from_user.id, "Выбери, пожалуйста, номер одного из пользователей.")
        elif len(inf[1]) == 0 or not (check_str(inf[1])):
            bot.send_message(message.from_user.id, "Слово должно состоять только из русских строчных букв. "
                                                   "Пожалуйста, напиши сообщение снова.")
        else:
            step = 1
            player_id = 0

            cur_name = cur_name_define(message.from_user.first_name, message.from_user.last_name)

            for item in sorted_dict:
                if item[1].name != cur_name:
                    if step == num_player:
                        player_id = int(item[0])
                        break
                    step += 1

            print(player_id)
            game = Game()

            all_users[player_id] = game
            all_users[player_id].game_on = True

            game.key_word = inf[1]
            game.hide_word = "*" * len(game.key_word)
            game.group = message.from_user.id

            bot.send_message(player_id, f"Пользователь {cur_name} загадал(а) тебе слово из {len(game.key_word)} "
                                        f"букв.\nВот оно: {game.hide_word}.\nТвоя задача: угадать все буквы, совершив "
                                        f"не более 8 ошибок.\nУдачи!")

            bot.send_message(message.from_user.id, f"Ты загадал(а) пользователю {results[str(player_id)].name} слово "
                                                   f"{game.key_word}.\n")


bot.polling(none_stop=True, interval=0)

