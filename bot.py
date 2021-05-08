import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import config
from loader import dp, db

send_email = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Отмена", callback_data="cancel_send"),
        InlineKeyboardButton(text="Подтвердить", callback_data="confirm_send")
    ]
])

admin_panel = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Список почт", callback_data="list_emails"),
        InlineKeyboardButton(text="Количество почт", callback_data="count_emails")
    ],
    [
        InlineKeyboardButton(text="Удалить все", callback_data="delete_emails"),
        InlineKeyboardButton(text="Отмена", callback_data="cancel")
    ]
])

delete_emails_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Отмена", callback_data="cancel"),
        InlineKeyboardButton(text="Подтвердить", callback_data="confirm_delete")
    ]
])


@dp.message_handler(user_id=config.ADMIN, text="/admin")
async def show_admin_panel(message: types.Message):
    await message.answer("Вы успешно открыли админ-панель.", reply_markup=admin_panel)


@dp.message_handler(CommandStart())
async def greeting(message: types.Message):
    await message.answer_video(video="BAACAgIAAxkBAAMEYJY3480OKcW6sxWy8og67uY5810AAnwNAAJgjrFIiU0P2ZPdQMwfBA",
                               caption="Оставьте свою почту.")  # В поле caption= можете сменить текст, но обязательно должен быть в ковычках.


@dp.message_handler()
async def confirmed_save_email(message: types.Message, state: FSMContext):
    all_users = await db.select_all_emails()
    users = []
    for user in all_users:
        users.append("{user_id}".format(**user))
    if not str(message.from_user.id) in users:
        await message.answer("Внимательно проверьте, правильно ли вы ввели свою почту, затем нажмите подтвердить.",  # Здесь также можно изменить текст.
                             reply_markup=send_email)
        await state.update_data(email=message.text)
        await state.set_state("confirmation_send")
    else:
        await message.answer("Ваша почта уже сохранена.")


@dp.callback_query_handler(state="confirmation_send", text="confirm_send")
async def save_email(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    email = data.get("email")
    id = await db.count_emails() + 1
    date = datetime.datetime.now()
    date_time = date.strftime("%m/%d/%Y  %H:%M")
    await db.add_email(id=id, user_id=call.from_user.id, email=email, datetime=date_time)
    await call.message.answer(
        "Ваша почта успешно сохранена! Ожидайте прилашения.")  # Здесь можете поменять текст, но он обязательно должен быть в ковычках.
    await call.message.edit_reply_markup()
    await state.reset_state()


@dp.callback_query_handler(state="confirmation_send", text="cancel_send")
async def cancel_email(call: types.CallbackQuery, state: FSMContext):
    await call.answer(text="Отмена", show_alert=True)
    await call.message.answer("Оставьте свою почту.")  # И здесь)
    await call.message.edit_reply_markup()
    await state.reset_state()


@dp.callback_query_handler(text="list_emails")
async def show_list_emails(call: types.CallbackQuery):
    count = await db.count_emails()
    all_emails = await db.select_all_emails()
    emails = ""
    for email in all_emails:
        emails += "{email} | {datetime}\n".format(**email)
    await call.answer()
    await call.message.answer(f"Список почт:\n\n{emails}\nВсего {count} почт")


@dp.callback_query_handler(text="count_emails")
async def show_count_emails(call: types.CallbackQuery):
    count = await db.count_emails()
    await call.answer()
    await call.message.answer(f"Количество почт: {count}")


@dp.callback_query_handler(text="delete_emails")
async def confirmation_delete(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer("Вы уверены, что хотите удалить все данные из базы данных?", reply_markup=delete_emails_keyboard)
    await state.set_state("confirmation_delete")


@dp.callback_query_handler(state="confirmation_delete", text="confirm_delete")
async def clear_table_emails(call: types.CallbackQuery, state: FSMContext):
    await db.delete_emails()
    await call.message.answer("Данные удалены.")
    await call.message.edit_reply_markup()
    await state.reset_state()


@dp.callback_query_handler(state="*", text="cancel")
async def cancel(call: types.CallbackQuery, state: FSMContext):
    await call.answer("Отмена", show_alert=True)
    await call.message.edit_reply_markup()
    await state.reset_state()
