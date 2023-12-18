import os
import discord
from discord.ext import commands
import json

# Use the 'token' key from config.json
discord_token = os.environ['token']

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!!", intents=intents)

# Load configuration from config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Ensure 'servers' key is present in config
if 'servers' not in config:
    config['servers'] = {}


# Group commands into a cog for better organization
class LinkCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='set')
    async def set_link(self, ctx, server_name, value):
        """Set a custom link for a custom server name."""
        config['servers'][server_name] = value
        with open('config.json', 'w') as config_file:
            json.dump(config, config_file)
        await ctx.send(f'Successfully set `{server_name}` link to: `{value}`')

    @commands.command(name='servers')
    async def list_servers(self, ctx):
        """List all servers names."""
        server_names = list(config['servers'].keys())
        if server_names:
            server_names_str = '\n'.join(
                f'{index + 1}. `{name}`'
                for index, name in enumerate(server_names))
            await ctx.send(f"Servers names:\n{server_names_str}")
        else:
            await ctx.send("No servers names found.")

    @commands.command(name='server_L')
    async def show_all_server_links(self, ctx):
        """Show links for all servers."""
        if config['servers']:
            for server_name, link in config['servers'].items():
                await ctx.send(f'`{server_name}` link: `{link}`')
        else:
            await ctx.send("No servers found.")


# Add the cog to the bot
@bot.event
async def on_ready():
    print(f'{bot.user} has connected')
    await bot.add_cog(LinkCommands(bot))


# Respond with the link when the custom server name or command is mentioned
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Check if the message starts with '!!' and is a custom server name
    if message.content.startswith('!!'):
        server_name = message.content[2:]  # Remove '!!' prefix
        link = config['servers'].get(server_name)
        if link is not None:
            await message.channel.send(f'`{server_name}` link: `{link}`')

    await bot.process_commands(message)


# Customize the help command
bot.remove_command('help')  # Remove the default help command


@bot.command(name='help')
async def custom_help(ctx, *args):
    """Custom help command."""
    if not args:
        # Display general help message
        help_message = (
            "Type `!!help command` for more info on a command.\n"
            "You can also type `!!set Name Link` for set server link.\n"
            "You can also type `!!servers` to list all servers names.\n"
            "You can also type `!!server_L` to show links for all servers.\n"
            "You can also type `!!help category` for more info on a category.")
        await ctx.send(help_message)
    else:
        # Display specific command help
        command = bot.get_command(args[0])
        if command:
            command_help = f"**{command.name}:** {command.help}"
            await ctx.send(command_help)
        else:
            await ctx.send("Command not found.")


# Suppress "Command not found" for any unknown command related to custom servers names
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        if ctx.message.content.startswith('!!'):
            return  # Ignore the error for custom servers names
    await ctx.send("Command not found.")


bot.run(discord_token)
