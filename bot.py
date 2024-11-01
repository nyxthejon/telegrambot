import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import logging
import random
from datetime import datetime

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Mock database
user_balances = {}

class GambleBot:
    def __init__(self):
        # Bot token
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            raise ValueError("No token provided!")

    # /start command
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        user_balances[user.id] = user_balances.get(user.id, 1000)  # Default starting balance
        welcome_message = (
            f" Welcome {user.mention_html()}!\n\n"
            "Available commands:\n"
            "/start - Show this welcome message\n"
            "/balance - Check your current balance\n"
            "/bet [amount] - Place a bet on a coin flip (double or lose)\n"
            "/addfunds [amount] - Add funds to your balance\n"
            "/withdraw [amount] - Withdraw funds from your balance\n"
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

            # Simulate coin flip (random number 1 or 2)
            coin_flip = random.randint(1, 2)

            if coin_flip == 1:  # Heads (win)
                user_balances[user.id] += bet_amount
                result_message = f"Heads! You win ${bet_amount}!"
            else:  # Tails (lose)
                user_balances[user.id] -= bet_amount
                result_message = f"Tails! You lose ${bet_amount}."

            await update.message.reply_text(
                f"Bet placed: ${bet_amount}\n"
                f"{result_message}\n"
                f"New balance: ${user_balances[user.id]}"
            )

        except ValueError:
            await update.message.reply_text("Please enter a valid number!")

    # /addfunds command
    async def addfunds_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if not context.args:
            await update.message.reply_text("Please specify amount to add: /addfunds [amount]")
            return

        try:
            add_amount = int(context.args[0])
            if add_amount <= 0:
                await update.message.reply_text("Amount must be positive!")
                return

            user_balances[user.id] += add_amount
            await update.message.reply_text(f"Added ${add_amount} to your balance. New balance: ${user_balances[user.id]}")

        except ValueError:
            await update.message.reply_text("Please enter a valid number!")

    # /withdraw command
    async def withdraw_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if not context.args:
            await update.message.reply_text("Please specify amount to withdraw: /withdraw [amount]")
            return

        try:
            withdraw_amount = int(context.args[0])
            if withdraw_amount <= 0:
                await update.message.reply_text("Amount must be positive!")
                return

            current_balance = user_balances.get(user.id, 0)
            if withdraw_amount > current_balance:
                await update.message.reply_text("Insufficient balance!")
                return

            user_balances[user.id] -= withdraw_amount
            await update.message.reply_text(f"Withdrew ${withdraw_amount}. New balance: ${user_balances[user.id]}")

        except ValueError:
            await update.message.reply_text("Please enter a valid number!")

    def run(self):
        application = Application.builder().token(self.token).build()
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("balance", self.balance_command))
        application.add_handler(CommandHandler("bet", self.bet_command))
        application.add_handler(CommandHandler("addfunds", self.addfunds_command))
        application.add_handler(CommandHandler("withdraw", self.withdraw_command))
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    bot = GambleBot()
    bot.run()