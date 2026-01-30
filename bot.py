import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from state import get_questions
from questions import (
    FUN_QUESTIONS,
    WOULD_YOU_RATHER,
    NEVER_HAVE_I_EVER,
    SITUATION_DILEMMA,
    RED_GREEN_FLAG,
    HOT_TAKES,
    FINISH_THE_SENTENCE,
)

TOKEN = "8505367284:AAEWRMjSboCZDLKuccdyb5IAqUmDTEgry1I"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------- CONFIG --------------------

CATEGORY_MAP = {
    "fun": FUN_QUESTIONS,
    "wyr": WOULD_YOU_RATHER,
    "never": NEVER_HAVE_I_EVER,
    "situation": SITUATION_DILEMMA,
    "flag": RED_GREEN_FLAG,
    "hot": HOT_TAKES,
    "finish": FINISH_THE_SENTENCE,
}

INTRO_LINES = {
    "fun": "🎉 Let’s warm things up:",
    "wyr": "🤔 Choose wisely:",
    "never": "🙅 Be honest… no judgement:",
    "situation": "🧠 Think carefully:",
    "flag": "🚩 Red or 🟢 Green? Debate it:",
    "hot": "🔥 Hot takes incoming:",
    "finish": "💬 Finish the sentence:",
}

DRAW_COUNTS = {
    "fun": 10,
    "wyr": 10,
    "never": 10,
    "flag": 10,
    "hot": 8,
    "situation": 5,
    "finish": 5,
}

MENU_TEXT = (
    "👀 Silence detected...\n\n"
    "I’m *Jennie*.\n"
    "Pick your poison and let’s revive this conversation 😏"
)

MENU_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("🎉 Fun Questions", callback_data="fun")],
    [InlineKeyboardButton("🤔 Would You Rather", callback_data="wyr")],
    [InlineKeyboardButton("🙅 Never Have I Ever", callback_data="never")],
    [InlineKeyboardButton("🧠 Situation Dilemma", callback_data="situation")],
    [InlineKeyboardButton("🚩 Red / 🟢 Green Flag", callback_data="flag")],
    [InlineKeyboardButton("🔥 Hot Takes", callback_data="hot")],
    [InlineKeyboardButton("💬 Finish the Sentence", callback_data="finish")],
    [InlineKeyboardButton("❌ Nevermind", callback_data="cancel")],
])

# -------------------- /START (ONBOARDING) --------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hey! Nice to meet you.\n\n"
        "I’m *Jennie* — I jump in when conversations go quiet 😏\n\n"
        "When you’re ready, type 👉 `/start_jennie` "
        "and I’ll drop some fun conversation prompts.",
        parse_mode="Markdown",
    )

# -------------------- /START_JENNIE (MENU) --------------------

async def start_jennie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Menu should exist only once
    if context.chat_data.get("menu_msg_id"):
        return

    msg = await update.message.reply_text(
        MENU_TEXT,
        reply_markup=MENU_KEYBOARD,
        parse_mode="Markdown",
    )

    context.chat_data["menu_msg_id"] = msg.message_id

# -------------------- BUTTON HANDLER --------------------

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id

    # ---------- NEVERMIND ----------
    if query.data == "cancel":
        q_id = context.chat_data.get("question_msg_id")
        m_id = context.chat_data.get("menu_msg_id")

        if q_id:
            try:
                await context.bot.delete_message(chat_id, q_id)
            except:
                pass

        if m_id:
            try:
                await context.bot.delete_message(chat_id, m_id)
            except:
                pass

        context.chat_data.clear()
        return

    # ---------- QUESTIONS ----------
    questions = CATEGORY_MAP.get(query.data)
    if not questions:
        return

    selected = get_questions(
        context.chat_data,
        query.data,
        questions,
        DRAW_COUNTS[query.data],
    )

    text = f"{INTRO_LINES[query.data]}\n\n"
    for i, q in enumerate(selected, 1):
        text += f"{i}. {q}\n"

    text += "\n💬 Discuss. Argue. Overshare."

    q_id = context.chat_data.get("question_msg_id")

    # Replace existing questions
    if q_id:
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=q_id,
                text=text
            )
            return
        except:
            pass

    # First time showing questions
    msg = await query.message.reply_text(text)
    context.chat_data["question_msg_id"] = msg.message_id

# -------------------- FALLBACK --------------------

async def fallback_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        await update.message.reply_text(
            "👋 Hey! I’m **Jennie**.\n\n"
            "When things get quiet, type `/start_jennie` "
            "and I’ll help get the conversation going 😏",
            parse_mode="Markdown",
        )

# -------------------- MAIN --------------------

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("start_jennie", start_jennie))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback_message))

    print("🤖 Jennie is running...")
    app.run_polling(close_loop=False)

if __name__ == "__main__":
    main()
