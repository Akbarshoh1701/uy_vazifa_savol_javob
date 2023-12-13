from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from states.register import RegisterState, AdminAnswerState
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from loader import bot

from loader import dp


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await message.answer(f"Salom menga savolingiz bo'lsa ismingizni yuboring")
    await RegisterState.name.set()


contakt = ReplyKeyboardMarkup(
    [
        [KeyboardButton("Orqaga"), KeyboardButton("contact", request_contact=True)]
    ],
    resize_keyboard=True
)


@dp.message_handler(text="Orqaga", state="*")
async def bot_start(message: types.Message):
    await message.answer(f"Salom menga savolingiz bo'lsa ismingizni yuboring",
                         reply_markup=types.ReplyKeyboardRemove())
    await RegisterState.name.set()


@dp.message_handler(state=RegisterState.name)
async def get_user_name(message: types.Message, state: FSMContext):
    name = message.text
    await state.update_data(name=name)
    await message.answer(f"Salom {name} telefon raqamingizni yuboring", reply_markup=contakt)

    await RegisterState.next()


@dp.message_handler(state=RegisterState.phone, content_types=types.ContentType.CONTACT)
async def get_user_phone(message: types.Message, state: FSMContext):
    contact = message.contact
    phone = contact.phone_number
    await state.update_data(phone=phone)
    await message.answer(f"telefon raqam qabul qilindi\nEndi savolingizni yuboring",
                         reply_markup=types.ReplyKeyboardRemove())
    await RegisterState.next()


@dp.message_handler(state=RegisterState.ask)
async def get_user_ask(message: types.Message, state: FSMContext):
    ask = message.text
    data = await state.get_data()
    await message.answer("Sizning savolingiz qabul qilindi ✅ admin javobini kuting")
    await state.finish()

    yes_or_no = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Javob berish", callback_data=f"user_id-{message.from_user.id}"),
                InlineKeyboardButton(text="atkaz", callback_data=f"atkaz-{message.from_user.id}")
            ]
        ]
    )

    await bot.send_message(chat_id=5865333668, text=f"Yangi savol"
                                                    f"\nIsmi: {data.get('name')}"
                                                    f"\nTelefon raqami: {data.get('phone')}"
                                                    f"\nSavoli: {ask}", reply_markup=yes_or_no)


@dp.callback_query_handler(lambda call: call.data.startswith("user_id"))
async def get_user_id(call: types.CallbackQuery, state: FSMContext):
    user_id = call.data.split("-")[-1]
    await state.update_data(user_id=user_id)
    await call.message.answer(f"Javobni yozing")
    await AdminAnswerState.user_id.set()


@dp.message_handler(state=AdminAnswerState.user_id)
async def get_admin_answer(message: types.Message, state: FSMContext):
    answer = message.text
    user_id = await state.get_data()
    await state.finish()
    await bot.send_message(chat_id=user_id.get('user_id'), text=f"admindan javob keldi"
                                                                f"\n{answer}")
    await message.answer("Javob yuborildi")


@dp.callback_query_handler(lambda call: call.data.startswith("atkaz"))
async def get_user_id(call: types.CallbackQuery, state: FSMContext):
    user_id = call.data.split("-")[-1]
    await state.update_data(user_id=user_id)
    await bot.send_message(chat_id=user_id, text=f"❌admin sizning savolingizga javob bermadi❌")
