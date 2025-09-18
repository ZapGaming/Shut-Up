import discord
import os
import asyncio
from flask import Flask, render_template_string
from gevent.pywsgi import WSGIServer
from gevent import monkey
import threading

monkey.patch_all()

# Retrieve bot token from environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Check for environment variables
if not DISCORD_TOKEN:
    print("Error: DISCORD_TOKEN environment variable is not set.")
    exit(1)

# Define the intents for the bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Create the bot client
bot = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(bot)

# Create the Flask web server instance
app = Flask(__name__)

# HTML for the "supercool" website
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Shutup Bot - The Ultimate Annoyance</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #1f2937, #111827);
        }
    </style>
</head>
<body class="text-white min-h-screen flex items-center justify-center p-4">
    <div class="bg-gray-800 p-8 rounded-2xl shadow-2xl max-w-xl w-full text-center border border-gray-700">
        <h1 class="text-5xl font-extrabold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-red-400 to-red-600">
            Shutup Bot
        </h1>
        <p class="text-xl text-gray-300 mb-8 leading-relaxed">
            A bot with one simple, yet powerful command: to make someone quiet.
        </p>
        <div class="bg-gray-900 p-6 rounded-xl shadow-inner border border-gray-700">
            <h2 class="text-3xl font-bold mb-4 text-red-500">The Command</h2>
            <code class="text-red-400 font-mono text-lg p-2 rounded-lg bg-gray-700 block">
                /shutup &lt;user&gt;
            </code>
            <p class="mt-4 text-gray-400">
                This command will mention the specified user 100 times in the channel. A small delay is added between each mention to prevent rate-limiting.
            </p>
            <p class="mt-2 text-sm text-gray-500 italic">
                (This command is restricted to users with the 'Manage Messages' permission.)
            </p>
        </div>
        <div class="mt-8">
            <a href="https://discord.com/developers/applications" target="_blank" class="inline-block py-3 px-8 text-lg font-semibold rounded-full shadow-lg transition-transform transform hover:scale-105 bg-red-600 hover:bg-red-500 focus:outline-none focus:ring-4 focus:ring-red-500 focus:ring-opacity-50">
                Get Your Own Bot
            </a>
        </div>
    </div>
</body>
</html>
"""

# Define the web server route
@app.route('/')
def home():
    """Renders the website for the bot."""
    return render_template_string(HTML_TEMPLATE)

@bot.event
async def on_ready():
    """
    Event that runs when the bot is connected to Discord.
    It synchronizes the command tree globally.
    """
    print(f'Logged in as {bot.user}')
    # Sync the command tree globally. This can take up to an hour to appear.
    await tree.sync()
    print('Commands synced globally.')

@tree.command(
    name="shutup",
    description="Makes the bot mention the specified user 100 times."
)
@discord.app_commands.checks.has_permissions(manage_messages=True)
async def shutup(interaction: discord.Interaction, user: discord.Member):
    """
    A slash command to mention a user 100 times.
    This command can only be used by users with the "Manage Messages" permission.

    Args:
        interaction: The interaction object.
        user: The user to be mentioned.
    """
    # Defer the interaction response so the user knows the command is being processed
    await interaction.response.defer(ephemeral=True)
    
    # Loop 100 times to send the mention
    for _ in range(100):
        # A small delay to prevent rate-limiting
        await asyncio.sleep(1)
        # Send the mention
        await interaction.channel.send(f"{user.mention}")

# Error handler for the command
@shutup.error
async def on_shutup_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    if isinstance(error, discord.app_commands.MissingPermissions):
        await interaction.response.send_message(
            "You don't have permission to use this command. You need the 'Manage Messages' permission.", 
            ephemeral=True
        )
    else:
        await interaction.response.send_message(f"An error occurred: {error}", ephemeral=True)

# Function to run the bot
def run_bot():
    bot.run(DISCORD_TOKEN)

# Main entry point to start both the web server and the bot
if __name__ == "__main__":
    # Start the bot in a separate thread
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    # Get the port from the environment and start the web server
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting web server on port {port}...")
    http_server = WSGIServer(('0.0.0.0', port), app)
    http_server.serve_forever()
