import discord
from discord.ext import commands
import sqlite3
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def generate_key(length=12):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def send_email(client_email, key):
    sender_email = EMAIL_SENDER
    sender_password = EMAIL_PASSWORD
    subject = "Bienvenue chez Digital Dynamics Studio !"

    with open("email_welcome_template.html", "r") as file:
        html_content = file.read()

    html_content = html_content.replace("{{ key }}", key)

    msg = MIMEMultipart("alternative")
    msg['From'] = sender_email
    msg['To'] = client_email
    msg['Subject'] = subject

    part1 = MIMEText(html_content, "html")
    msg.attach(part1)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, client_email, text)
        server.quit()
        print(f"Email envoyé à {client_email}")
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email : {e}")

def validate_date(date_text):
    try:
        date = datetime.strptime(date_text, '%d/%m/%Y')
        return date
    except ValueError:
        return None

class ClientManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client_creation_data = {}
        self.allowed_channel_id = 1267789734868947034

    @commands.command()
    async def creation(self, ctx):
        print("Commande !creation appelée")
        if ctx.channel.id != self.allowed_channel_id:
            await ctx.send("Cette commande ne peut être utilisée que dans le canal autorisé.")
            return

        if not ctx.channel.permissions_for(ctx.author).manage_channels:
            await ctx.send("Vous n'avez pas la permission d'utiliser cette commande.")
            return

        self.client_creation_data[ctx.author.id] = {}
        await ctx.send("Entrez le nom du client :")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=60)
            self.client_creation_data[ctx.author.id]['name'] = msg.content
            await ctx.send("Entrez le nom de l'entreprise :")

            msg = await self.bot.wait_for('message', check=check, timeout=60)
            self.client_creation_data[ctx.author.id]['company'] = msg.content
            await ctx.send("Entrez l'email du client :")

            msg = await self.bot.wait_for('message', check=check, timeout=60)
            self.client_creation_data[ctx.author.id]['email'] = msg.content
            await ctx.send("Entrez le numéro de téléphone du client :")

            msg = await self.bot.wait_for('message', check=check, timeout=60)
            self.client_creation_data[ctx.author.id]['phone'] = msg.content
            await ctx.send("Entrez le nom du projet :")

            msg = await self.bot.wait_for('message', check=check, timeout=60)
            self.client_creation_data[ctx.author.id]['project_name'] = msg.content
            await ctx.send("Entrez la description du projet :")

            msg = await self.bot.wait_for('message', check=check, timeout=60)
            self.client_creation_data[ctx.author.id]['project_description'] = msg.content
            await ctx.send("Entrez la date de la première visio (jours/mois/année) :")

            valid_date = None
            while not valid_date:
                msg = await self.bot.wait_for('message', check=check, timeout=60)
                valid_date = validate_date(msg.content)
                if not valid_date:
                    await ctx.send("Date invalide. Veuillez entrer une date au format jours/mois/année :")
            self.client_creation_data[ctx.author.id]['visio_date'] = valid_date.strftime('%d/%m/%Y')

            key = generate_key()
            self.client_creation_data[ctx.author.id]['key'] = key

            conn = sqlite3.connect('clients.db')
            c = conn.cursor()
            c.execute("INSERT INTO clients (name, company, email, phone, project_name, project_description, key, visio_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                      (self.client_creation_data[ctx.author.id]['name'],
                       self.client_creation_data[ctx.author.id]['company'],
                       self.client_creation_data[ctx.author.id]['email'],
                       self.client_creation_data[ctx.author.id]['phone'],
                       self.client_creation_data[ctx.author.id]['project_name'],
                       self.client_creation_data[ctx.author.id]['project_description'],
                       self.client_creation_data[ctx.author.id]['key'],
                       self.client_creation_data[ctx.author.id]['visio_date']))
            conn.commit()
            conn.close()

            send_email(self.client_creation_data[ctx.author.id]['email'], key)
            await ctx.send(f"Client ajouté et clé envoyée à {self.client_creation_data[ctx.author.id]['email']}")

            del self.client_creation_data[ctx.author.id]

        except Exception as e:
            await ctx.send("Temps écoulé ou erreur. Veuillez réessayer.")
            if ctx.author.id in self.client_creation_data:
                del self.client_creation_data[ctx.author.id]
            print(f"Erreur lors de l'exécution de la commande : {e}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await member.send("Bienvenue ! Veuillez entrer votre clé d'accès :")

        def check(m):
            return m.author == member and isinstance(m.channel, discord.DMChannel)

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=60)
            key = msg.content

            conn = sqlite3.connect('clients.db')
            c = conn.cursor()
            c.execute("SELECT * FROM clients WHERE key=?", (key,))
            client = c.fetchone()
            conn.close()

            if client:
                await member.send("Veuillez entrer votre adresse email pour vérification :")
                msg = await self.bot.wait_for('message', check=check, timeout=60)
                email = msg.content

                if email == client[3]:  # Vérification de l'email
                    guild = member.guild

                    role = discord.utils.get(guild.roles, name="Client")
                    if role is not None:
                        await member.add_roles(role)
                    else:
                        await member.send("Le rôle 'Client' n'existe pas. Veuillez contacter un administrateur.")

                    if guild.me.guild_permissions.manage_channels:
                        # Créer une catégorie et des canaux pour le projet
                        overwrites = {
                            guild.default_role: discord.PermissionOverwrite(read_messages=False),
                            member: discord.PermissionOverwrite(read_messages=True)
                        }
                        category = await guild.create_category(f"{client[5]} - {client[2]}" , overwrites=overwrites)
                        await guild.create_text_channel('général', category=category)
                        await guild.create_text_channel('planning', category=category)
                        await guild.create_text_channel('discussion', category=category)
                        await guild.create_text_channel('notification-trello', category=category)
                        await guild.create_text_channel('notification-github', category=category)
                        await guild.create_voice_channel('visio', category=category)

                        # Envoyer un message de bienvenue
                        welcome_message = f"Bienvenue {client[1]} ! Votre projet '{client[5]}' a été configuré. La date de votre première visio est fixée au {client[8]}."
                        await member.send(welcome_message)

                        # Supprimer la clé après utilisation
                        conn = sqlite3.connect('clients.db')
                        c = conn.cursor()
                        c.execute("UPDATE clients SET key=NULL WHERE key=?", (key,))
                        conn.commit()
                        conn.close()
                    else:
                        await member.send("Je n'ai pas la permission de créer des canaux. Veuillez contacter un administrateur.")
                else:
                    await member.send("Adresse email incorrecte. Veuillez contacter un administrateur.")
            else:
                await member.send("Clé invalide. Veuillez contacter un administrateur.")
        except Exception as e:
            await member.send("Temps écoulé ou erreur. Veuillez réessayer.")
            print(e)

async def setup(bot):
    await bot.add_cog(ClientManagement(bot))
