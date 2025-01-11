from handlers.default import TestStates, tests, answers_num, start_list
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram import Router
from keyboards import make_2col_keyboard
import json



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

        await message.answer(f"Тест завершен. У вас {correct} правильных ответов из {len(answers)}!",
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
