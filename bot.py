import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.enums import ContentType
from datetime import datetime
import json
import os
import asyncio

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

API_TOKEN = os.getenv('API_TOKEN', '')
GROUP_CHAT_ID = int(os.getenv('GROUP_CHAT_ID', '0'))
CARS_FILE = os.getenv('CARS_FILE', 'cars.json')
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]

logging.basicConfig(level=logging.INFO)

# Инициализация бота с хранилищем состояний
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Структура для хранения сообщений из канала
channel_posts = []

# Тексты для меню
MENU_TEXT = "Выберите действие:"

INFO_TEXT = (
    'Корейские автомобили под заказ: красота, комфорт и надежность прямо к вам. '
    'Группа для тех, кто ценит стиль и качество!\n\n'
    'Предоставляет услуги подбора, оценки и перегонки автомобилей.\n\n'
    'Наша команда профессионалов поможет вам выбрать подходящий автомобиль, '
    'сделает полноценный фотоотчет и видеоотчет его состояния и безопасно доставит его вам.\n\n'
    'Мы гарантируем качественное обслуживание и надежность в каждом этапе работы с нами.'
)

CONTACT_TEXT = (
    'Связь с администраторами по поиску авто:\n'
    '- @badaim98\n'
    '- @naimzhon42'
)

PAY_TEXT = (
    '🌟 Условия оплаты заказа автомобиля из Кореи:\n\n'
    '1. *Договор*\n'
    'Заключаем официальный договор купли-продажи, в котором прописаны все условия заказа, '
    'оплаты, перегонки и гарантии.\n\n'
    '2. *Предоплата*\n'
    'При оформлении заказа необходимо внести предоплату в размере 80% от стоимости автомобиля. '
    'Это позволит нам начать процесс подбора и перегонки автомобиля.\n\n'
    '3. *Оставшиеся 20% при получении*\n'
    'Оставшиеся 20% оплачиваются при получении автомобиля. Таким образом, вы можете убедиться '
    'в состоянии и качестве автомобиля перед полной оплатой.\n\n'
    '💲 Стоимость автомобиля зависит от текущего курса доллара. Мы рассчитываем стоимость '
    'по актуальному курсу на момент оплаты.\n\n'
    '✨ *Выгодная цена, без посредников*\n'
    'При сотрудничестве с нами вы получаете возможность приобрести автомобиль из Кореи по '
    'выгодной цене, без дополнительных наценок со стороны посредников.\n\n'
    '✨ Предлагаем гибкие условия оплаты, чтобы сделать процесс заказа автомобиля из Кореи '
    'максимально удобным для вас. Ваш комфорт и уверенность - наш главный приоритет! 🚗💵\n\n'
    '✨ Мы придаем большое значение прозрачности и законности во всех этапах сотрудничества, '
    'поэтому заключение официального договора дает вам дополнительную гарантию и уверенность '
    'в проведении сделки.\n\n'
    'Если у вас есть дополнительные вопросы или требуется дальнейшая консультация по условиям '
    'заказа и оплаты, не стесняйтесь обращаться к нам:\n'
    'tel:+79526406618\n'
    'tel:+79024718290'
)

DELIVERY_TEXT = (
    '🌟 Условия заказа автомобиля из Кореи:\n\n'
    '1. *Подбор*\n'
    'Предоставляем персональный подбор автомобиля с учетом ваших пожеланий и требований '
    'к автомобилю.\n\n'
    '2. *Видеоотчет*\n'
    'После нахождения подходящего автомобиля, мы предоставляем подробный видеоотчет о его '
    'состоянии, чтобы вы могли увидеть все детали.\n\n'
    '3. *Гарантия*\n'
    'Автомобили поставляются с гарантией качества. Мы гарантируем подлинность и исправность '
    'каждого автомобиля, отправляющегося на перегон.\n\n'
    '4. *Перегон*\n'
    'Мы занимаемся перегоном автомобилей из Кореи без посредников, обеспечивая безопасную '
    'доставку автомобиля прямо к вам.\n\n'
    '✨ Наша команда готова сделать процесс заказа автомобиля из Кореи максимально удобным '
    'и прозрачным для вас. Обращайтесь к нам для получения высококачественного сервиса и '
    'надежной доставки вашего будущего автомобиля! 🚗🌏\n\n'
    'Мы всегда на связи для консультации и начала заказа:\n'
    'tel:+79526406618\n'
    'tel:+79024718290\n\n'
    'Доверьте нам ваш выбор!'
)

# Клавиатуры
def get_reply_keyboard():
    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="📋 Меню")]], resize_keyboard=True)
    return keyboard

def get_main_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🚗 Доступные авто", callback_data="show_cars"),
            InlineKeyboardButton(text="📦 Доставка", callback_data="delivery")
        ],
        [
            InlineKeyboardButton(text="📞 Контакты", callback_data="contact"),
            InlineKeyboardButton(text="💰 Оплата", callback_data="pay")
        ],
        [
            InlineKeyboardButton(text="ℹ️ Информация", callback_data="info")
        ]
    ])
    return keyboard

def get_back_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="menu")]
    ])
    return keyboard

# Обработчики команд
@dp.message(Command("start", "help"))
async def send_welcome(message: types.Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}!\n{MENU_TEXT}",
        reply_markup=get_reply_keyboard()
    )
    await message.answer(
        reply_markup=get_main_menu()
    )

@dp.message(F.text == "📋 Меню")
async def process_menu_button(message: types.Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}!\n{MENU_TEXT}",
        reply_markup=get_reply_keyboard()
    )
    await message.answer(
        "Выберите действие:",
        reply_markup=get_main_menu()
    )

# Обработчики callback-запросов
@dp.callback_query(F.data == "menu")
async def process_menu(callback_query: types.CallbackQuery):
    print(f"[DEBUG] Callback from user {callback_query.from_user.id} ({callback_query.from_user.username}): {callback_query.data}")
    await callback_query.message.edit_text(
        MENU_TEXT,
        reply_markup=get_main_menu()
    )

@dp.callback_query(F.data == "show_cars")
async def process_show_cars(callback_query: types.CallbackQuery):
    print(f"[DEBUG] Callback from user {callback_query.from_user.id} ({callback_query.from_user.username}): {callback_query.data}")
    cars = load_cars()
    print('[DEBUG] cars.json содержимое при show_cars:', cars)
    if not cars:
        await callback_query.message.edit_text(
            "Пока нет доступных автомобилей",
            reply_markup=get_back_menu()
        )
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for brand in cars:
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=brand, callback_data=f'user_brand_{brand}')])
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data="menu")])
    await callback_query.message.edit_text(
        "Выберите марку:",
        reply_markup=keyboard
    )

@dp.callback_query(F.data.startswith("post_"))
async def process_post(callback_query: types.CallbackQuery):
    print(f"[DEBUG] Callback from user {callback_query.from_user.id} ({callback_query.from_user.username}): {callback_query.data}")
    message_id = int(callback_query.data.split('_')[1])
    post = next((p for p in channel_posts if p['message_id'] == message_id), None)
    
    if post:
        # Создаем ссылку на сообщение в канале
        channel_link = f"https://t.me/c/{str(GROUP_CHAT_ID)[4:]}/{message_id}"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔗 Открыть в канале", url=channel_link)],
            [InlineKeyboardButton(text="◀️ Назад к списку", callback_data="show_cars")]
        ])
        
        await callback_query.message.edit_text(
            f"📅 Дата публикации: {post['date']}\n\n"
            f"Перейдите по ссылке ниже, чтобы посмотреть полное описание автомобиля:",
            reply_markup=keyboard
        )
    else:
        await callback_query.message.edit_text(
            "Сообщение не найдено",
            reply_markup=get_back_menu()
        )

@dp.callback_query(F.data == "contact")
async def process_contact(callback_query: types.CallbackQuery):
    print(f"[DEBUG] Callback from user {callback_query.from_user.id} ({callback_query.from_user.username}): {callback_query.data}")
    await callback_query.message.edit_text(
        CONTACT_TEXT,
        reply_markup=get_back_menu()
    )

@dp.callback_query(F.data == "pay")
async def process_pay(callback_query: types.CallbackQuery):
    print(f"[DEBUG] Callback from user {callback_query.from_user.id} ({callback_query.from_user.username}): {callback_query.data}")
    await callback_query.message.edit_text(
        PAY_TEXT,
        reply_markup=get_back_menu()
    )

@dp.callback_query(F.data == "info")
async def process_info(callback_query: types.CallbackQuery):
    print(f"[DEBUG] Callback from user {callback_query.from_user.id} ({callback_query.from_user.username}): {callback_query.data}")
    await callback_query.message.edit_text(
        INFO_TEXT,
        reply_markup=get_back_menu()
    )

@dp.callback_query(F.data == "delivery")
async def process_delivery(callback_query: types.CallbackQuery):
    print(f"[DEBUG] Callback from user {callback_query.from_user.id} ({callback_query.from_user.username}): {callback_query.data}")
    await callback_query.message.edit_text(
        DELIVERY_TEXT,
        reply_markup=get_back_menu()
    )

@dp.callback_query(F.data == "start")
async def process_start(callback_query: types.CallbackQuery):
    print(f"[DEBUG] Callback from user {callback_query.from_user.id} ({callback_query.from_user.username}): {callback_query.data}")
    await callback_query.message.edit_text(
        f"Привет, {callback_query.from_user.first_name}!\n{MENU_TEXT}",
        reply_markup=get_main_menu()
    )

# Обработчик новых сообщений из группы
@dp.message(F.chat.id == GROUP_CHAT_ID)
async def new_group_post(message: types.Message):
    print(f"[DEBUG] Сработал group handler! chat_id: {message.chat.id}, user: {message.from_user.id} ({message.from_user.username}), text: {message.text if message.text else 'нет текста'}")
    post_info = {
        'message_id': message.message_id,
        'date': datetime.now().strftime("%d.%m.%Y"),
        'chat_id': message.chat.id
    }
    channel_posts.append(post_info)
    if len(channel_posts) > 100:
        channel_posts.pop(0)

@dp.channel_post()
async def channel_post_handler(message: types.Message):
    print(f"[DEBUG] channel_post! chat_id: {message.chat.id}, text: {message.text if message.text else 'нет текста'}")
    await message.reply(f"channel chat_id: {message.chat.id}")

# FSM для добавления
class AddCarFSM(StatesGroup):
    waiting_for_brand = State()
    waiting_for_model = State()
    waiting_for_car_title = State()
    waiting_for_car_url = State()

# Загрузка/сохранение данных
def load_cars():
    if not os.path.exists(CARS_FILE):
        return {}
    with open(CARS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_cars(data):
    with open(CARS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Новое админ-меню
@dp.message(Command("admin"))
async def admin_menu(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='➕ Добавить авто', callback_data='admin_addcar')],
        [InlineKeyboardButton(text='🗑 Удалить авто', callback_data='admin_delete_cars')],
        [InlineKeyboardButton(text='📋 Список всех авто', callback_data='admin_list_all')]
    ])
    await message.answer('Админ-меню:', reply_markup=keyboard)

@dp.callback_query(F.data == "admin_addcar")
async def admin_addcar_callback(callback_query: types.CallbackQuery):
    if callback_query.from_user.id not in ADMIN_IDS:
        return
    await callback_query.message.delete()
    await addcar_start(callback_query.message)
    await callback_query.answer()

@dp.callback_query(F.data == "admin_delete_cars")
async def admin_delete_cars_callback(callback_query: types.CallbackQuery):
    if callback_query.from_user.id not in ADMIN_IDS:
        return
    cars = load_cars()
    if not cars:
        await callback_query.message.answer('Нет автомобилей для удаления.')
        await callback_query.answer()
        return
    
    # Создаем список всех автомобилей для удаления
    all_cars = []
    for brand in cars:
        for model in cars[brand]:
            for idx, car in enumerate(cars[brand][model]):
                all_cars.append({
                    'brand': brand,
                    'model': model,
                    'idx': idx,
                    'title': car['title']
                })
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for car in all_cars:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"🗑 {car['brand']} {car['model']} - {car['title']}", 
                callback_data=f'admin_delete_{car["brand"]}_{car["model"]}_{car["idx"]}'
            )
        ])
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data="admin_back")])
    
    await callback_query.message.edit_text(
        f'Выберите автомобиль для удаления (всего: {len(all_cars)}):',
        reply_markup=keyboard
    )
    await callback_query.answer()

@dp.callback_query(F.data.startswith("admin_delete_"))
async def admin_delete_car(callback_query: types.CallbackQuery):
    if callback_query.from_user.id not in ADMIN_IDS:
        return
    _, _, brand, model, idx = callback_query.data.split('_', 4)
    idx = int(idx)
    cars = load_cars()
    
    if brand in cars and model in cars[brand] and 0 <= idx < len(cars[brand][model]):
        removed_car = cars[brand][model].pop(idx)
        
        # Удаляем пустые модели и марки
        if not cars[brand][model]:
            del cars[brand][model]
        if not cars[brand]:
            del cars[brand]
        
        save_cars(cars)
        await callback_query.message.answer(f'✅ Удалено: {brand} {model} - {removed_car["title"]}')
        
        # Обновляем список
        await admin_delete_cars_callback(callback_query)
    else:
        await callback_query.message.answer('❌ Ошибка при удалении.')
    await callback_query.answer()

@dp.callback_query(F.data == "admin_list_all")
async def admin_list_all_callback(callback_query: types.CallbackQuery):
    if callback_query.from_user.id not in ADMIN_IDS:
        return
    cars = load_cars()
    if not cars:
        await callback_query.message.answer('Нет добавленных авто.')
        await callback_query.answer()
        return
    
    # Создаем список всех автомобилей
    all_cars = []
    for brand in cars:
        for model in cars[brand]:
            for car in cars[brand][model]:
                all_cars.append(f"• {brand} {model} - {car['title']}")
    
    cars_text = '\n'.join(all_cars)
    await callback_query.message.answer(f'📋 Все автомобили ({len(all_cars)}):\n\n{cars_text}')
    await callback_query.answer()

@dp.callback_query(F.data == "admin_back")
async def admin_back_callback(callback_query: types.CallbackQuery):
    if callback_query.from_user.id not in ADMIN_IDS:
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='➕ Добавить авто', callback_data='admin_addcar')],
        [InlineKeyboardButton(text='🗑 Удалить авто', callback_data='admin_delete_cars')],
        [InlineKeyboardButton(text='📋 Список всех авто', callback_data='admin_list_all')]
    ])
    await callback_query.message.edit_text('Админ-меню:', reply_markup=keyboard)
    await callback_query.answer()

# Пользовательское меню: выбор марки, модели, авто
@dp.message(F.text == "🚗 Доступные авто")
async def user_show_brands(message: types.Message):
    cars = load_cars()
    print('[DEBUG] cars.json содержимое при открытии меню:', cars)
    if not cars:
        await message.answer('Пока нет доступных марок.')
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for brand in cars:
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=brand, callback_data=f'user_brand_{brand}')])
    await message.answer('Выберите марку:', reply_markup=keyboard)

@dp.callback_query(F.data.startswith("user_brand_"))
async def user_show_models(callback_query: types.CallbackQuery):
    brand = callback_query.data.replace('user_brand_', '')
    cars = load_cars()
    models = cars.get(brand, {})
    if not models:
        await callback_query.message.answer('Пока нет моделей у этой марки.')
        await callback_query.answer()
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for model in models:
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=model, callback_data=f'user_model_{brand}_{model}')])
    await callback_query.message.answer('Выберите модель:', reply_markup=keyboard)
    await callback_query.answer()

@dp.callback_query(F.data.startswith("user_model_"))
async def user_show_cars(callback_query: types.CallbackQuery):
    _, _, brand, model = callback_query.data.split('_', 3)
    cars = load_cars()
    car_list = cars.get(brand, {}).get(model, [])
    if not car_list:
        await callback_query.message.answer('Пока нет авто у этой модели.')
        await callback_query.answer()
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for car in car_list:
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=car['title'], url=car['url'])])
    await callback_query.message.answer('Выберите авто:', reply_markup=keyboard)
    await callback_query.answer()

class AddCarSimpleFSM(StatesGroup):
    waiting_for_brand = State()
    waiting_for_model = State()
    waiting_for_title = State()
    waiting_for_url = State()

@dp.message(Command("addcar"))
async def addcar_start(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    await message.answer('Введите марку:')
    await dp.storage.set_state(user=message.from_user.id, state=AddCarSimpleFSM.waiting_for_brand)

@dp.message(AddCarSimpleFSM.waiting_for_brand)
async def addcar_brand(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    await state.update_data(brand=message.text.strip())
    await message.answer('Введите модель:')
    await state.set_state(AddCarSimpleFSM.waiting_for_model)

@dp.message(AddCarSimpleFSM.waiting_for_model)
async def addcar_model(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    await state.update_data(model=message.text.strip())
    await message.answer('Введите название кнопки')
    await state.set_state(AddCarSimpleFSM.waiting_for_title)

@dp.message(AddCarSimpleFSM.waiting_for_title)
async def addcar_title(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    await state.update_data(title=message.text.strip())
    await message.answer('Вставьте ссылку на пост в Telegram (https://t.me/c/...):')
    await state.set_state(AddCarSimpleFSM.waiting_for_url)

@dp.message(AddCarSimpleFSM.waiting_for_url)
async def addcar_url(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    data = await state.get_data()
    brand = data['brand']
    model = data['model']
    title = data['title']
    url = message.text.strip()
    if not (url.startswith('http://') or url.startswith('https://')):
        await message.answer('Ошибка! Ссылка должна начинаться с http:// или https://. Введите ссылку ещё раз:')
        return
    cars = load_cars()
    if brand not in cars:
        cars[brand] = {}
    if model not in cars[brand]:
        cars[brand][model] = []
    cars[brand][model].append({'title': title, 'url': url})
    save_cars(cars)
    await message.answer(f'Авто "{title}" добавлено в {brand} / {model}!')
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main()) 
