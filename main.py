#1 IMPORTS
import discord
from discord.ext import commands
from discord import app_commands
import json
import random
import os

#2 BOT SETUP
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="yako", intents=intents)

#3 LOAD / SAVE DATA
def load_data():
    if os.path.exists("data.json"):
        with open("data.json", "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

#4 GET BALANCE
def get_balance(user_id):
    user_id = str(user_id)
    if user_id not in data:
        data[user_id] = {"coins": 0, "energy": 20}
        save_data(data)
    return data[user_id]

#5 SLASH: BALANCE
@bot.tree.command(name="balance", description="Check your coin balance.")
async def balance(interaction: discord.Interaction):
    user = get_balance(interaction.user.id)
    await interaction.response.send_message(f"You have **{user['coins']}** coins.")

#6 SLASH: ADDCOIN (OWNER ONLY)
@bot.tree.command(name="addcoin", description="Owner only: add coins to a user.")
@app_commands.describe(user="User to give coins", amount="Amount to give")
async def addcoin(interaction: discord.Interaction, user: discord.Member, amount: int):

    owner_id = 1239592428239982704  # YOUR ID

    if interaction.user.id != owner_id:
        await interaction.response.send_message("You are NOT allowed.", ephemeral=True)
        return

    target = get_balance(user.id)
    target["coins"] += amount
    save_data(data)

    await interaction.response.send_message(
        f"Added **{amount}** coins to **{user.name}**."
    )

#7 WORK SYSTEM VALUES
energy_cost = {
    "cutting_log": (2, 8),
    "farming": (1, 6),
    "fishing": (2, 4)
}

rewards = {
    "cutting_log": (230, 600),
    "farming": (134, 271),
    "fishing": (20, 1000)
}

#8 SLASH: WORK
@bot.tree.command(name="work", description="Work to earn coins.")
@app_commands.describe(job="Choose a job: cutting_log / farming / fishing")
async def work(interaction: discord.Interaction, job: str):

    job = job.lower()
    if job not in energy_cost:
        await interaction.response.send_message(
            "Invalid job! Choose: cutting_log, farming, fishing."
        )
        return

    user = get_balance(interaction.user.id)

    # ENERGY CHECK
    if user["energy"] <= 0:
        await interaction.response.send_message("You have **0 energy**. You cannot work anymore today!")
        return

    # RANDOM ENERGY USED
    min_e, max_e = energy_cost[job]
    used_energy = random.randint(min_e, max_e)

    if used_energy > user["energy"]:
        used_energy = user["energy"]  # Use remaining energy

    user["energy"] -= used_energy

    # RANDOM REWARD
    min_r, max_r = rewards[job]
    reward = random.randint(min_r, max_r)

    user["coins"] += reward
    save_data(data)

    await interaction.response.send_message(
        f"You worked **{job.replace('_', ' ')}**!\n"
        f"Reward: **{reward}** coins\n"
        f"Energy used: **{used_energy}**\n"
        f"Your current energy: **{user['energy']}**"
    )

#9 BOT READY
@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Bot is ready.")
from keep_alive import keep_alive
keep_alive()
#10 RUN BOT
bot.run(os.getenv("TOKEN"))