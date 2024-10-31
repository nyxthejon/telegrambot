import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import logging
from datetime import datetime

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Mock database
user_balances = {}

class GambleBot:
    def __init__(self):
        #Bot token
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            raise ValueError("No token provided!")

    # /start command
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        user_balances[user.id] = user_balances.get(user.id, 1000)  # Default starting balance
        welcome_message = (
            f"👋 Welcome {user.mention_html()}!\n\n"
            "Available commands:\n"
            "/start - Show this welcome message\n"
            "/balance - Check your current balance\n"
            "/bet [amount] - Place a bet\n"
        )
        await update.message.reply_html(welcome_message)

    # /balance command
    async def balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        balance = user_balances.get(user.id, 0)
        await update.message.reply_text(f"Your current balance: ${balance}")

    # /bet command
    async def bet_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if not context.args:
            await update.message.reply_text("Please specify bet amount: /bet [amount]")
            return

        try:
            bet_amount = int(context.args[0])
            if bet_amount <= 0:
                await update.message.reply_text("Bet amount must be positive!")
                return

            current_balance = user_balances.get(user.id, 0)
            if bet_amount > current_balance:
                await update.message.reply_text("Insufficient balance!")
                return

            await update.message.reply_text(
                f"Bet placed: ${bet_amount}\n"
            )

        except ValueError:
            await update.message.reply_text("Please enter a valid number!")

    def run(self):
        application = Application.builder().token(self.token).build()
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("balance", self.balance_command))
        application.add_handler(CommandHandler("bet", self.bet_command))
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    bot = GambleBot()
    bot.run()