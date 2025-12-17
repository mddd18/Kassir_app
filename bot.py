# ============================
# KASSIR BOT 2025 — TUZATILGAN VERSIYA
# Funksiyalar: Qo'shish | Tahrirlash | O'chirish | Sotish | Hisobot
# ============================

import os
import json
import asyncio
from datetime import datetime
from collections import Counter

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery, ReplyKeyboardRemove,
    KeyboardButton, ReplyKeyboardMarkup,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# Fayllar
PRODUCTS_FILE = "products.json"
SALES_FILE = "sales.json"

# O'zingizning tokeningizni shu yerga yozing yoki .env ga o'tkazing
BOT_TOKEN = "8389715287:AAEluJCahLEPIUEfVMKngfltgBlY4Youkr8"

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

# Ma'lumotlar
products = []
sales_data = []
product_id_counter = 1
user_carts = {}  # {user_id: {"items": [], "total": 0}}
user_languages = {}  # {user_id: "uz" / "qq"}

# Tillar
TEXTS = {
    "uz": {
        "welcome": "<b>Kassir Bot 2025 ga xush kelibsiz!</b>\n\nTilni tanlang:",
        "lang_selected": "Til o'zbekcha tangildi ✅",
        "menu_add": "Yangi o'nim qo'shish",
        "menu_sell": "Sotish",
        "menu_list": "O'nimlar ro'yxati",
        "menu_delete": "O'nim o'chirish",
        "menu_edit": "Mahsulot tahrirlash",
        "menu_report": "Hisobot",
        "menu_history": "Sotuvlar tarixi",
        "menu_exit": "Chiqish",
        "menu_settings": "⚙️ Sozlamalar",
        "enter_name": "O'nim nomini kiriting:",
        "enter_cost": "Tannarx (so'mda):",
        "enter_profit": "Foyda foizi (%):",
        "enter_quantity": "Nechta dona keldi?",
        "added": "<b>Qo'shildi!</b>",
        "price": "Narxi",
        "stock": "Qoldiq",
        "cancel": "Bekor qilish",
        "cancelled": "Bekor qilindi",
        "invalid_number": "Faqat raqam kiriting!",
        "edit_price": "Narxini o'zgartirmoqchi bo'lgan mahsulotni tanlang:",
        "current_price": "Hozirgi narxi",
        "new_price": "Yangi narxni kiriting (so'mda):",
        "updated": "<b>Muvaffaqiyatli o'zgartirildi!</b>",
        "old_price": "Eski narx",
        "new_price_label": "Yangi narx",
        "no_products": "Hozircha mahsulot yo'q!",
        "available_products": "<b>Mavjud o'nimlar:</b>",
        "empty_shop": "Do'kon bo'sh",
        "delete_product": "O'chiriladigan o'nim:",
        "deleted": "o'chirildi!",
        "not_found": "Topilmadi",
        "select": "Tanlang:",
        "cart": "Savat",
        "sold_out": "Tugagan!",
        "empty_cart": "Savat bo'sh!",
        "payment": "To'lov",
        "back": "Orqaga",
        "payment_accepted": "<b>TO'LOV QABUL QILINDI!</b>\n\n<b>{total:,.0f} so'm</b>\n\nRahmat!",
        "sell_again": "Yana sotish uchun tugmani bosing",
        "sale_cancelled": "Sotuv bekor qilindi",
        "main_menu": "Bosh menyu",
        "report_title": "<b>📊 HISOBOT</b>",
        "total_income": "Jami daromad",
        "checks_count": "Cheklar soni",
        "most_sold": "Eng ko'p sotilgan",
        "no_sales": "Hech qanday sotuv yo'q",
        "history_title": "<b>📊 SOTUVLAR TARIXI</b>\n\nKunni tanlang:",
        "select_date": "Kunni tanlang:",
        "clear_history": "🗑 Tarixni tozalash",
        "no_sales_today": "Bu kunda sotuv yo'q",
        "check": "Chek",
        "daily_total": "Kunlik jami",
        "warning": "<b>⚠️ DIQQAT!</b>\n\nBarcha sotuvlar tarixini o'chirmoqchimisiz?\nBu amalni qaytarib bo'lmaydi!",
        "yes_clear": "✅ Ha, tozalash",
        "no": "❌ Yo'q",
        "history_cleared": "✅ Sotuvlar tarixi tozalandi!",
        "history_closed": "Tarix yopildi",
        "exit_msg": "Botdan chiqdingiz. Xayr!",
        "error_not_enough": "Xatolik: {name} yetarli emas!",
        "save": "Saqlash",
        "ta": "ta",
        "som": "so'm"
    },
    "qq": {
        "welcome": "<b>Kassir Bot 2025 ge xosh kelibsiz!</b>\n\nTildi saylań:",
        "lang_selected": "Til qaraqalpaqsha saylandı ✅",
        "menu_add": "Jańa tawır qosıw",
        "menu_sell": "Satıw",
        "menu_list": "Tawırlar dizimi",
        "menu_delete": "Tawır óshiriw",
        "menu_edit": "Maxsulot tázeletiw",
        "menu_report": "Bayannama",
        "menu_history": "Satıw tariyxı",
        "menu_exit": "Shıǵıw",
        "menu_settings": "⚙️ Sazlawlar",
        "enter_name": "Tawır atın kiritiń:",
        "enter_cost": "Tannarx (sumnan):",
        "enter_profit": "Payda payzı (%):",
        "enter_quantity": "Neshe dana keldi?",
        "added": "<b>Qosıldı!</b>",
        "price": "Bahası",
        "stock": "Qaldıq",
        "cancel": "Biykar ettiw",
        "cancelled": "Biykar etildi",
        "invalid_number": "Tek san kiritiń!",
        "edit_price": "Bahasın ózgertkińiz kelgen maxsulotnı saylań:",
        "current_price": "Házirgi bahası",
        "new_price": "Jańa bahanı kiritiń (sumnan):",
        "updated": "<b>Tabıslı ózgertildi!</b>",
        "old_price": "Eski baha",
        "new_price_label": "Jańa baha",
        "no_products": "Házir maxsulot joq!",
        "available_products": "<b>Bar tawırlar:</b>",
        "empty_shop": "Dúkan bos",
        "delete_product": "Óshiriletug̀ın tawır:",
        "deleted": "óshirildi!",
        "not_found": "Tabılmadı",
        "select": "Saylań:",
        "cart": "Sebetim",
        "sold_out": "Bitip kettı!",
        "empty_cart": "Sebetim bos!",
        "payment": "Tólem",
        "back": "Artqa",
        "payment_accepted": "<b>TÓLEM QABIL ETILDI!</b>\n\n<b>{total:,.0f} sum</b>\n\nRaxmet!",
        "sell_again": "Jańadan satıw ushın basıń",
        "sale_cancelled": "Satıw biykar etildi",
        "main_menu": "Bas menyu",
        "report_title": "<b>📊 BAYANNAMA</b>",
        "total_income": "Jámi kiristi",
        "checks_count": "Chekler sanı",
        "most_sold": "Eń kóp satılǵan",
        "no_sales": "Hesh qanday satıw joq",
        "history_title": "<b>📊 SATIWLAR TARIYXI</b>\n\nKúndi saylań:",
        "select_date": "Kúndi saylań:",
        "clear_history": "🗑 Tariyxtı tazalaw",
        "no_sales_today": "Bul kúnde satıw joq",
        "check": "Chek",
        "daily_total": "Kúnlik jámi",
        "warning": "<b>⚠️ DIQQAT!</b>\n\nBarlıq satıw tariyxın óshiresiz be?\nBul ámeldı qaytarıw múmkin emes!",
        "yes_clear": "✅ Awa, tazalaw",
        "no": "❌ Joq",
        "history_cleared": "✅ Satıw tariyxı tazalandı!",
        "history_closed": "Tarıyx jabıldı",
        "exit_msg": "Bottan shıqtıńız. Xayır!",
        "error_not_enough": "Qátelik: {name} jeterli emes!",
        "save": "Saqlash",
        "ta": "dana",
        "som": "sum"
    }
}

def get_text(user_id, key):
    """Foydalanuvchi tiliga qarab matn qaytaradi"""
    lang = user_languages.get(user_id, "uz")
    return TEXTS[lang].get(key, TEXTS["uz"][key])

# Yuklash va saqlash
def load_data():
    global products, sales_data, product_id_counter
    try:
        if os.path.exists(PRODUCTS_FILE):
            with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
                products = json.load(f)
        if os.path.exists(SALES_FILE):
            with open(SALES_FILE, "r", encoding="utf-8") as f:
                sales_data = json.load(f)
        if products:
            product_id_counter = max(p["id"] for p in products) + 1
    except Exception as e:
        print("Yuklashda xato:", e)

def save_data():
    try:
        with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        with open(SALES_FILE, "w", encoding="utf-8") as f:
            json.dump(sales_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Saqlashda xato:", e)

load_data()

# States
class AddProduct(StatesGroup):
    name = State()
    cost_price = State()
    profit_percent = State()
    quantity = State()

class EditProduct(StatesGroup):
    select = State()       # mahsulot tanlash
    price = State()        # faqat narx

# Asosiy menu
def main_menu(user_id):
    t = lambda k: get_text(user_id, k)
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=t("menu_add"))],
        [KeyboardButton(text=t("menu_sell")), KeyboardButton(text=t("menu_list"))],
        [KeyboardButton(text=t("menu_delete")), KeyboardButton(text=t("menu_edit"))],
        [KeyboardButton(text=t("menu_report")), KeyboardButton(text=t("menu_history"))],
        [KeyboardButton(text=t("menu_settings")), KeyboardButton(text=t("menu_exit"))]
    ], resize_keyboard=True)

# Til tanlash
def language_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="O'zbekcha", callback_data="lang_uz")],
        [InlineKeyboardButton(text="Qaraqalpaqsha", callback_data="lang_qq")]
    ])

# START
@router.message(Command("start"))
async def start(message: Message):
    await message.answer(get_text(message.from_user.id, "welcome"), reply_markup=language_keyboard())

# Til tanlash
@router.callback_query(F.data.startswith("lang_"))
async def select_language(cb: CallbackQuery):
    lang = cb.data.split("_")[1]
    user_languages[cb.from_user.id] = lang
    await cb.message.edit_text(get_text(cb.from_user.id, "lang_selected"))
    await cb.message.answer(get_text(cb.from_user.id, "main_menu"), reply_markup=main_menu(cb.from_user.id))
    await cb.answer()

# Sozlamalar (til o'zgartirish)
@router.message(F.text.in_(["⚙️ Sozlamalar", "⚙️ Sazlawlar"]))
async def settings(message: Message):
    await message.answer(get_text(message.from_user.id, "welcome"), reply_markup=language_keyboard())

# ═══════════════════ YANGI O'NIM QO'SHISH ═══════════════════
@router.message(F.text.in_(["Yangi o'nim qo'shish", "Jańa tawır qosıw"]))
async def cmd_add(message: Message, state: FSMContext):
    t = lambda k: get_text(message.from_user.id, k)
    await message.answer(t("enter_name"), reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t("cancel"))]], resize_keyboard=True))
    await state.set_state(AddProduct.name)

@router.message(AddProduct.name)
async def add_name(message: Message, state: FSMContext):
    t = lambda k: get_text(message.from_user.id, k)
    if message.text in [t("cancel"), "Bekor qilish", "Biykar ettiw"]:
        await state.clear()
        await message.answer(t("cancelled"), reply_markup=main_menu(message.from_user.id))
        return
    await state.update_data(name=message.text.strip())
    await message.answer(t("enter_cost"))
    await state.set_state(AddProduct.cost_price)

@router.message(AddProduct.cost_price)
async def add_cost(message: Message, state: FSMContext):
    t = lambda k: get_text(message.from_user.id, k)
    if message.text in [t("cancel"), "Bekor qilish", "Biykar ettiw"]:
        await state.clear()
        await message.answer(t("cancelled"), reply_markup=main_menu(message.from_user.id))
        return
    try:
        cost = float(message.text.replace(",", "."))
        if cost <= 0: raise ValueError
        await state.update_data(cost_price=cost)
        await message.answer(t("enter_profit"))
        await state.set_state(AddProduct.profit_percent)
    except:
        await message.answer(t("invalid_number"))

@router.message(AddProduct.profit_percent)
async def add_profit(message: Message, state: FSMContext):
    t = lambda k: get_text(message.from_user.id, k)
    if message.text in [t("cancel"), "Bekor qilish", "Biykar ettiw"]:
        await state.clear()
        await message.answer(t("cancelled"), reply_markup=main_menu(message.from_user.id))
        return
    try:
        profit = float(message.text)
        await state.update_data(profit_percent=profit)
        await message.answer(t("enter_quantity"))
        await state.set_state(AddProduct.quantity)
    except:
        await message.answer(t("invalid_number"))

@router.message(AddProduct.quantity)
async def add_quantity(message: Message, state: FSMContext):
    global product_id_counter
    t = lambda k: get_text(message.from_user.id, k)
    if message.text in [t("cancel"), "Bekor qilish", "Biykar ettiw"]:
        await state.clear()
        await message.answer(t("cancelled"), reply_markup=main_menu(message.from_user.id))
        return
    try:
        qty = int(message.text)
        if qty < 1: raise ValueError
        data = await state.get_data()
        price = data["cost_price"] * (1 + data["profit_percent"] / 100)

        products.append({
            "id": product_id_counter,
            "name": data["name"].capitalize(),
            "price": round(price),
            "sani": qty
        })
        product_id_counter += 1
        save_data()

        await message.answer(
            f"{t('added')}\n\n"
            f"<b>{data['name'].capitalize()}</b>\n"
            f"{t('price')}: <b>{price:,.0f} {t('som')}</b>\n"
            f"{t('stock')}: <b>{qty}</b> {t('ta')}",
            reply_markup=main_menu(message.from_user.id)
        )
        await state.clear()
    except:
        await message.answer(t("invalid_number"))

# ═══════════════════ MAHSULOT TAHRIRLASH (FAQAT NARX) ═══════════════════
@router.message(F.text.in_(["Mahsulot tahrirlash", "Maxsulot tázeletiw"]))
async def edit_start(message: Message, state: FSMContext):
    t = lambda k: get_text(message.from_user.id, k)
    if not products:
        await message.answer(t("no_products"), reply_markup=main_menu(message.from_user.id))
        return

    kb = []
    for p in products:
        kb.append([InlineKeyboardButton(
            text=f"{p['name']} — {p['price']:,.0f} {t('som')} ({p['sani']} {t('ta')})",
            callback_data=f"editselect_{p['id']}"
        )])
    kb.append([InlineKeyboardButton(text=t("cancel"), callback_data="cancel_edit")])

    await message.answer(t("edit_price"), 
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await state.set_state(EditProduct.select)

@router.callback_query(F.data.startswith("editselect_"))
async def edit_selected(cb: CallbackQuery, state: FSMContext):
    pid = int(cb.data.split("_")[1])
    product = next((p for p in products if p["id"] == pid), None)
    if not product:
        await cb.answer(get_text(cb.from_user.id, "not_found"))
        return

    t = lambda k: get_text(cb.from_user.id, k)
    await state.update_data(edit_id=pid)
    text = (f"<b>{product['name']}</b>\n\n"
            f"{t('current_price')}: <b>{product['price']:,.0f} {t('som')}</b>\n"
            f"{t('stock')}: <b>{product['sani']} {t('ta')}</b>\n\n"
            f"<b>{t('new_price')}</b>")

    await cb.message.edit_text(text)
    await cb.message.answer(t("new_price"), reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t("cancel"))]], resize_keyboard=True))
    await state.set_state(EditProduct.price)
    await cb.answer()

@router.message(EditProduct.price)
async def edit_price_save(message: Message, state: FSMContext):
    t = lambda k: get_text(message.from_user.id, k)
    if message.text in [t("cancel"), "Bekor qilish", "Biykar ettiw"]:
        await state.clear()
        await message.answer(t("cancelled"), reply_markup=main_menu(message.from_user.id))
        return

    try:
        price = int(message.text.replace(" ", "").replace(",", ""))
        if price <= 0: raise ValueError

        data = await state.get_data()
        pid = data["edit_id"]

        for p in products:
            if p["id"] == pid:
                old_price = p["price"]
                p["price"] = price
                product_name = p["name"]
                quantity = p["sani"]
                break

        save_data()
        await message.answer(
            f"{t('updated')}\n\n"
            f"<b>{product_name}</b>\n"
            f"{t('old_price')}: <s>{old_price:,.0f} {t('som')}</s>\n"
            f"{t('new_price_label')}: <b>{price:,.0f} {t('som')}</b>\n"
            f"{t('stock')}: <b>{quantity} {t('ta')}</b>",
            reply_markup=main_menu(message.from_user.id)
        )
        await state.clear()
    except:
        await message.answer(t("invalid_number"))

@router.callback_query(F.data == "cancel_edit")
async def cancel_edit(cb: CallbackQuery, state: FSMContext):
    t = lambda k: get_text(cb.from_user.id, k)
    await state.clear()
    await cb.message.edit_text(t("cancelled"))
    await cb.message.answer(t("main_menu"), reply_markup=main_menu(cb.from_user.id))

# ═══════════════════ O'NIMLAR RO'YXATI ═══════════════════
@router.message(F.text.in_(["O'nimlar ro'yxati", "Tawırlar dizimi"]))
async def list_products(message: Message):
    t = lambda k: get_text(message.from_user.id, k)
    if not products:
        return await message.answer(t("empty_shop"), reply_markup=main_menu(message.from_user.id))
    text = f"{t('available_products')}\n\n"
    for p in products:
        text += f"• {p['name']} — {p['price']:,.0f} {t('som')} ({p['sani']} {t('ta')})\n"
    await message.answer(text, reply_markup=main_menu(message.from_user.id))

# ═══════════════════ O'CHIRISH ═══════════════════
@router.message(F.text.in_(["O'nim o'chirish", "Tawır óshiriw"]))
async def delete_start(message: Message):
    t = lambda k: get_text(message.from_user.id, k)
    if not products:
        return await message.answer(t("no_products"), reply_markup=main_menu(message.from_user.id))
    kb = [[InlineKeyboardButton(text=f"{p['name']} ({p['sani']} {t('ta')})", callback_data=f"del_{p['id']}")] for p in products]
    kb.append([InlineKeyboardButton(text=t("cancel"), callback_data="cancel_delete")])
    await message.answer(t("delete_product"), reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@router.callback_query(F.data.startswith("del_"))
async def delete_confirm(cb: CallbackQuery):
    t = lambda k: get_text(cb.from_user.id, k)
    pid = int(cb.data.split("_")[1])
    for p in products[:]:
        if p["id"] == pid:
            name = p["name"]
            products.remove(p)
            save_data()
            await cb.message.edit_text(f"<b>{name}</b> {t('deleted')}")
            await cb.message.answer(t("main_menu"), reply_markup=main_menu(cb.from_user.id))
            await cb.answer()
            return
    await cb.answer(t("not_found"))

@router.callback_query(F.data == "cancel_delete")
async def cancel_delete(cb: CallbackQuery):
    t = lambda k: get_text(cb.from_user.id, k)
    await cb.message.edit_text(t("cancelled"))
    await cb.message.answer(t("main_menu"), reply_markup=main_menu(cb.from_user.id))

# ═══════════════════ SOTISH (TUZATILGAN) ═══════════════════
@router.message(F.text.in_(["Sotish", "Satıw"]))
async def sell_start(message: Message):
    t = lambda k: get_text(message.from_user.id, k)
    if not products:
        return await message.answer(t("empty_shop"), reply_markup=main_menu(message.from_user.id))
    user_carts[message.from_user.id] = {"items": [], "total": 0}
    await show_sell_menu(message)

async def show_sell_menu(msg):
    user_id = msg.from_user.id if isinstance(msg, Message) else msg.message.chat.id
    t = lambda k: get_text(user_id, k)
    kb = []
    for p in products:
        if p["sani"] > 0:
            kb.append([InlineKeyboardButton(
                text=f"{p['name']} — {p['price']:,.0f} {t('som')} ({p['sani']} {t('ta')})",
                callback_data=f"buy_{p['id']}"
            )])
    kb.append([InlineKeyboardButton(text=t("cart"), callback_data="cart")])
    kb.append([InlineKeyboardButton(text=t("cancel"), callback_data="cancel")])

    if isinstance(msg, Message):
        await msg.answer(t("select"), reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    else:
        await msg.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@router.callback_query(F.data.startswith("buy_"))
async def buy_item(cb: CallbackQuery):
    t = lambda k: get_text(cb.from_user.id, k)
    pid = int(cb.data.split("_")[1])
    p = next((x for x in products if x["id"] == pid), None)
    if not p or p["sani"] <= 0:
        await cb.answer(t("sold_out"), show_alert=True)
        return

    cart = user_carts.get(cb.from_user.id, {"items": [], "total": 0})
    cart["items"].append({"id": p["id"], "name": p["name"], "price": p["price"]})
    cart["total"] += p["price"]
    user_carts[cb.from_user.id] = cart

    await cb.answer(f"+ {p['name']}", show_alert=True)
    await show_sell_menu(cb)

@router.callback_query(F.data == "cart")
async def show_cart(cb: CallbackQuery):
    t = lambda k: get_text(cb.from_user.id, k)
    cart = user_carts.get(cb.from_user.id)
    if not cart or not cart["items"]:
        await cb.answer(t("empty_cart"), show_alert=True)
        return

    counter = Counter(item["name"] for item in cart["items"])
    text = f"<b>{t('cart').upper()}</b>\n\n"
    total = 0
    for name, count in counter.items():
        price = next(item["price"] for item in cart["items"] if item["name"] == name)
        subtotal = price * count
        total += subtotal
        text += f"{name} × {count} = {subtotal:,.0f} {t('som')}\n"
    text += f"\n<b>JAMI: {total:,.0f} {t('som')}</b>"

    kb = [[InlineKeyboardButton(text=t("payment"), callback_data="pay")],
           [InlineKeyboardButton(text=t("back"), callback_data="back_sell")]]
    await cb.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@router.callback_query(F.data == "pay")
async def pay(cb: CallbackQuery):
    t = lambda k: get_text(cb.from_user.id, k)
    cart = user_carts.get(cb.from_user.id)
    if not cart or not cart["items"]:
        await cb.answer(t("empty_cart"))
        return

    counter = Counter(item["name"] for item in cart["items"])
    
    for name, count in counter.items():
        product = next((p for p in products if p["name"] == name), None)
        if not product or product["sani"] < count:
            await cb.answer(t("error_not_enough").format(name=name), show_alert=True)
            return
    
    sale_time = datetime.now().strftime("%d.%m.%Y %H:%M")
    sale_items = []
    
    for name, count in counter.items():
        product = next((p for p in products if p["name"] == name), None)
        if product:
            product["sani"] -= count
            price = next(item["price"] for item in cart["items"] if item["name"] == name)
            sale_items.append({
                "name": name,
                "quantity": count,
                "price": price,
                "total": price * count
            })
    
    sales_data.append({
        "items": sale_items,
        "total": cart["total"],
        "time": sale_time
    })

    total = cart["total"]
    save_data()
    await cb.message.edit_text(t("payment_accepted").format(total=total), reply_markup=None)
    await cb.message.answer(t("sell_again"), reply_markup=main_menu(cb.from_user.id))
    user_carts.pop(cb.from_user.id, None)

@router.callback_query(F.data.in_({"cancel", "back_sell"}))
async def cancel_sell(cb: CallbackQuery):
    t = lambda k: get_text(cb.from_user.id, k)
    user_carts.pop(cb.from_user.id, None)
    await cb.message.edit_text(t("sale_cancelled"))
    await cb.message.answer(t("main_menu"), reply_markup=main_menu(cb.from_user.id))

# ═══════════════════ HISOBOT ═══════════════════
@router.message(F.text.in_(["Hisobot", "Bayannama"]))
async def report(message: Message):
    t = lambda k: get_text(message.from_user.id, k)
    if not sales_data:
        return await message.answer(t("no_sales"), reply_markup=main_menu(message.from_user.id))

    total = sum(sale["total"] for sale in sales_data)
    
    all_items = []
    for sale in sales_data:
        for item in sale["items"]:
            all_items.extend([item["name"]] * item["quantity"])
    
    if all_items:
        most = Counter(all_items).most_common(1)[0]
        most_sold = f"<b>{most[0]}</b> ({most[1]} {t('ta')})"
    else:
        most_sold = "—"

    await message.answer(
        f"{t('report_title')}\n\n"
        f"{t('total_income')}: <b>{total:,.0f} {t('som')}</b>\n"
        f"{t('checks_count')}: <b>{len(sales_data)}</b> {t('ta')}\n"
        f"{t('most_sold')}: {most_sold}",
        reply_markup=main_menu(message.from_user.id)
    )

# ═══════════════════ SOTUVLAR TARIXI ═══════════════════
@router.message(F.text.in_(["Sotuvlar tarixi", "Satıw tariyxı"]))
async def sales_history(message: Message):
    t = lambda k: get_text(message.from_user.id, k)
    if not sales_data:
        return await message.answer(t("no_sales"), reply_markup=main_menu(message.from_user.id))
    
    sales_by_date = {}
    for sale in sales_data:
        date = sale["time"].split()[0]
        if date not in sales_by_date:
            sales_by_date[date] = []
        sales_by_date[date].append(sale)
    
    kb = []
    for date in sorted(sales_by_date.keys(), reverse=True):
        daily_total = sum(s["total"] for s in sales_by_date[date])
        daily_count = len(sales_by_date[date])
        kb.append([InlineKeyboardButton(
            text=f"📅 {date} — {daily_count} {t('check')} ({daily_total:,.0f} {t('som')})",
            callback_data=f"history_{date}"
        )])
    
    kb.append([InlineKeyboardButton(text=t("clear_history"), callback_data="clear_history")])
    kb.append([InlineKeyboardButton(text=f"◀️ {t('back')}", callback_data="close_history")])
    
    await message.answer(t("history_title"), reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@router.callback_query(F.data.startswith("history_"))
async def show_daily_sales(cb: CallbackQuery):
    t = lambda k: get_text(cb.from_user.id, k)
    date = cb.data.split("_", 1)[1]
    
    daily_sales = [s for s in sales_data if s["time"].startswith(date)]
    
    if not daily_sales:
        await cb.answer(t("no_sales_today"))
        return
    
    text = f"<b>📅 {date}</b>\n\n"
    daily_sales.sort(key=lambda x: x["time"])
    
    total_sum = 0
    for i, sale in enumerate(daily_sales, 1):
        time = sale["time"].split()[1]
        text += f"<b>{t('check')} #{i}</b> — {time}\n"
        
        for item in sale["items"]:
            text += f"  • {item['name']} × {item['quantity']} = {item['total']:,.0f} {t('som')}\n"
        
        text += f"  <b>Jami: {sale['total']:,.0f} {t('som')}</b>\n\n"
        total_sum += sale["total"]
    
    text += f"<b>{t('daily_total')}: {total_sum:,.0f} {t('som')}</b>\n"
    text += f"<b>{t('checks_count')}: {len(daily_sales)} {t('ta')}</b>"
    
    kb = [[InlineKeyboardButton(text=f"◀️ {t('back')}", callback_data="back_to_history")]]
    await cb.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@router.callback_query(F.data == "back_to_history")
async def back_to_history(cb: CallbackQuery):
    t = lambda k: get_text(cb.from_user.id, k)
    if not sales_data:
        await cb.message.edit_text(t("no_sales"))
        return
    
    sales_by_date = {}
    for sale in sales_data:
        date = sale["time"].split()[0]
        if date not in sales_by_date:
            sales_by_date[date] = []
        sales_by_date[date].append(sale)
    
    kb = []
    for date in sorted(sales_by_date.keys(), reverse=True):
        daily_total = sum(s["total"] for s in sales_by_date[date])
        daily_count = len(sales_by_date[date])
        kb.append([InlineKeyboardButton(
            text=f"📅 {date} — {daily_count} {t('check')} ({daily_total:,.0f} {t('som')})",
            callback_data=f"history_{date}"
        )])
    
    kb.append([InlineKeyboardButton(text=t("clear_history"), callback_data="clear_history")])
    kb.append([InlineKeyboardButton(text=f"◀️ {t('back')}", callback_data="close_history")])
    
    await cb.message.edit_text(t("history_title"), reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@router.callback_query(F.data == "clear_history")
async def confirm_clear(cb: CallbackQuery):
    t = lambda k: get_text(cb.from_user.id, k)
    kb = [
        [InlineKeyboardButton(text=t("yes_clear"), callback_data="confirm_clear")],
        [InlineKeyboardButton(text=t("no"), callback_data="back_to_history")]
    ]
    await cb.message.edit_text(t("warning"), reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@router.callback_query(F.data == "confirm_clear")
async def clear_history(cb: CallbackQuery):
    t = lambda k: get_text(cb.from_user.id, k)
    global sales_data
    sales_data = []
    save_data()
    
    await cb.message.edit_text(t("history_cleared"))
    await cb.message.answer(t("main_menu"), reply_markup=main_menu(cb.from_user.id))

@router.callback_query(F.data == "close_history")
async def close_history(cb: CallbackQuery):
    t = lambda k: get_text(cb.from_user.id, k)
    await cb.message.edit_text(t("history_closed"))
    await cb.message.answer(t("main_menu"), reply_markup=main_menu(cb.from_user.id))

# ═══════════════════ CHIQISH ═══════════════════
@router.message(F.text.in_(["Chiqish", "Shıǵıw"]))
async def chiqish(message: Message):
    t = lambda k: get_text(message.from_user.id, k)
    await message.answer(t("exit_msg"), reply_markup=ReplyKeyboardRemove())

# Ishga tushirish
dp.include_router(router)

if __name__ == "__main__":
    print("Kassir Bot 2025 ishga tushmoqda...")
    asyncio.run(dp.start_polling(bot))