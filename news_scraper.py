import discord
from discord.ext import commands
import sqlite3
from scraper import scrape_articles
import asyncio

class NewsScraper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='news')
    async def news(self, ctx):
        if ctx.channel.id != 1267855435390652427:
            await ctx.send("Vous ne pouvez utiliser cette commande que dans le canal autorisé.")
            return

        keywords = [
            "technology",
            "AI",
            "blockchain",
            "cybersecurity",
            "startups",
            "gadgets",
            "innovation",
            "software",
            "hardware",
            "science"
            "marketing",
            "social media",
            "digital",
            "neuromarketing"
        ]

        keyword_list = "\n".join([f"{i+1}. {keyword}" for i, keyword in enumerate(keywords)])
        await ctx.send(f"Merci de selectionner les mots clés par leur index séparé par une virgule (ex: 1,3,5):\n{keyword_list}")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            message = await self.bot.wait_for('message', check=check, timeout=60.0)
            selected_indices = [int(x.strip()) - 1 for x in message.content.split(',') if x.strip().isdigit()]

            valid_indices = [i for i in selected_indices if 0 <= i < len(keywords)]
            if not valid_indices:
                await ctx.send("Aucun mot clé valide sélectionné. Veuillez réessayer.")
                return

            selected_keywords = [keywords[i] for i in valid_indices]

            await ctx.send(f"Mots clés sélectionnés : {', '.join(selected_keywords)}")
            await self.fetch_and_display_articles(ctx, selected_keywords)

        except asyncio.TimeoutError:
            await ctx.send("Temps écoulé. Veuillez réessayer.")

    async def fetch_and_display_articles(self, ctx, keywords):
        conn = sqlite3.connect('clients.db')
        c = conn.cursor()

        articles = scrape_articles(keywords)
        print(f"Articles scraped: {articles}")  # Log the articles for debugging

        new_articles = []
        for article in articles:
            c.execute('SELECT * FROM articles WHERE url = ?', (article['url'],))
            if not c.fetchone():
                c.execute('INSERT INTO articles (title, url, summary) VALUES (?, ?, ?)',
                          (article['title'], article['url'], article['summary']))
                conn.commit()
                new_articles.append(article)

        if new_articles:
            for article in new_articles:
                await ctx.send(f"**{article['title']}**\n{article['summary']}\n{article['url']}")
        else:
            await ctx.send("Pas de nouveaux articles pour ce mot clé.")

        conn.close()

async def setup(bot):
    await bot.add_cog(NewsScraper(bot))
