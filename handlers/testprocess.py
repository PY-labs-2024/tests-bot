from handlers.default import TestStates, tests, answers_num, start_list
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram import Router
from keyboards import make_2col_keyboard
import json
import pandas as pd


def average_test_res(test_num: int):
    # открываем DF с записями о покупках
    df = pd.read_csv('data/answers.csv')
    # фильтруем DF по тесту
    df_filtered = df[(df['test_num'] == test_num)]

    return df_filtered['sum_correct'].mean()


def new_row_answers(user_id: int, answers, correct: int, test_num: int):
    # Проверяем, что список answers содержит ровно 10 элементов
    if len(answers) != 10:
        print(len(answers))
        raise ValueError("Список answers должен содержать ровно 10 элементов")

    # Загружаем существующий файл в DataFrame
    df = pd.read_csv('data/answers.csv')

    # Создаем новую строку с записями
    new_row = {
        'id': user_id,
        'test_num': test_num,
        'answer1': answers[0],
        'answer2': answers[1],
        'answer3': answers[2],
        'answer4': answers[3],
        'answer5': answers[4],
        'answer6': answers[5],
        'answer7': answers[6],
        'answer8': answers[7],
        'answer9': answers[8],
        'answer10': answers[9],
        'sum_correct': correct
    }

    # Добавляем новую строку в DataFrame
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # Сохраняем обновленный DataFrame обратно в файл
    df.to_csv('data/answers.csv', index=False)


tpr = Router()


@tpr.message(TestStates.waiting_for_test_number)
async def handle_test_selection(message: types.Message, state: FSMContext):
    test_name = message.text
    if test_name in tests:
        with open(f"data/test{test_name[-1]}.json", "r", encoding='utf-8') as my_file:
            json_test = my_file.read()
        test_base = json.loads(json_test)

        with open(f"data/correct_answers{test_name[-1]}.json", "r", encoding='utf-8') as my_file:
            json_answer = my_file.read()
        answer_base = json.loads(json_answer)

        await state.update_data(test_base=test_base)
        await state.update_data(answer_base=answer_base)
        await state.update_data(test_num=test_name[-1])
        await state.update_data(answers=[])
        await state.update_data(current_question=0)
        await state.update_data(correct=0)
        await ask_next_question(message, state)
    else:
        await message.answer("Пожалуйста, выберите тест из предложенных")


async def ask_next_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    current_test = data.get('test_base')
    current_question = data.get('current_question')

    if current_question < len(current_test):
        question = list(current_test)[current_question]
        tmp = question
        for i in range(4):
            tmp += (f"\n{i+1}) " + current_test[question][i])
        await message.answer(tmp, reply_markup=make_2col_keyboard(answers_num))
        await state.set_state(TestStates.waiting_for_answer)
    else:
        data = await state.get_data()
        answers = data.get("answers")
        correct = data.get("correct")
        test_num = data.get("test_num")

        new_row_answers(message.from_user.id, answers, correct, test_num)
        mean_sum = average_test_res(int(test_num))
        await message.answer(f"Тест завершен. У вас {correct} правильных ответов из {len(answers)}! "
                             f"В среднем этот тест проходят на {round(mean_sum, 2)}",
                             reply_markup=make_2col_keyboard(start_list))
        await state.set_state(TestStates.waiting_for_test_number)


@tpr.message(TestStates.waiting_for_answer)
async def handle_answer(message: types.Message, state: FSMContext):
    message_text = message.text
    if message_text not in answers_num:
        await message.answer("Некорректный ответ. Повторите ввод.",
                             reply_markup=make_2col_keyboard(answers_num))
    data = await state.get_data()
    current_test = data.get('test_base')
    current_question = data.get('current_question')
    question = list(current_test)[current_question]
    correct_answer = data.get('answer_base')[question]

    print(len(list(current_test)))
    answers = data.get('answers', [])
    answers.append(current_test[question][int(message.text)-1])
    await state.update_data(answers=answers)

    current_question = data.get('current_question') + 1
    await state.update_data(current_question=current_question)

    correct = data.get('correct')
    if correct_answer == current_test[question][int(message.text)-1]:
        correct += 1
        await state.update_data(correct=correct)
        await message.answer("Верно!")
    else:
        await message.answer(f"Неверно! Верный ответ: {correct_answer}")

    await ask_next_question(message, state)
