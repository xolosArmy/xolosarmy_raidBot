from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, filters
from collections import defaultdict

# Bot token from BotFather
bot_token = 'BOT_TOKEN'
bot = Bot(token=bot_token)
app = ApplicationBuilder().token(bot_token).build()

# Dictionary to store report counts
report_counts = defaultdict(int)
ban_threshold = 3  # Number of reports needed to trigger a ban

# Define the /raid command to send a raid message
async def raid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Extract the raid message from the command arguments
    if context.args:
        message = " ".join(context.args)
        # Send the message to the group
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"📢 RAID ALERT: {message}")
    else:
        await update.message.reply_text("Please provide a message to send with the raid.")

# Define the /report command to report a user
async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:  # Reported message must be a reply
        reported_user = update.message.reply_to_message.from_user
        reporter = update.message.from_user
        
        # Increase report count for the reported user
        report_counts[reported_user.id] += 1
        count = report_counts[reported_user.id]
        
        # Notify reporter and the group
        await update.message.reply_text(
            f"{reporter.first_name} reported {reported_user.first_name}. Total reports: {count}."
        )
        
        # Check if report count reached the threshold
        if count >= ban_threshold:
            # Ban the user and send goodbye message
            await context.bot.ban_chat_member(update.effective_chat.id, reported_user.id)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"👋 {reported_user.first_name} has been banned from the group for inappropriate behavior. Goodbye!"
            )
            # Reset the report count for the banned user
            report_counts[reported_user.id] = 0
    else:
        await update.message.reply_text("Please reply to the message of the user you'd like to report.")

# Define the /ban command for admins to manually ban users
async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        reported_user = update.message.reply_to_message.from_user
        if update.message.from_user.id in context.bot.get_chat_administrators(update.effective_chat.id):
            # Ban the user
            await context.bot.ban_chat_member(update.effective_chat.id, reported_user.id)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"👋 {reported_user.first_name} has been banned by an admin. Goodbye!"
            )
        else:
            await update.message.reply_text("Only admins can use this command.")
    else:
        await update.message.reply_text("Please reply to the message of the user you'd like to ban.")

# Define a /start command to introduce the bot
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm the XolosArmy Raid Bot. Use /raid <message> to start a raid, /report to report bad behavior, and /ban (admins only) to ban users.")

# Handlers for each command
app.add_handler(CommandHandler("raid", raid_command))
app.add_handler(CommandHandler("start", start_command))
app.add_handler(CommandHandler("report", report_command, filters=filters.REPLY))
app.add_handler(CommandHandler("ban", ban_command, filters=filters.REPLY))

# Start the bot
app.run_polling()
