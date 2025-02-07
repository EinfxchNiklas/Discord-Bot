import discord
from discord.ext import commands
import asyncio
import yt_dlp
from keep_alive import keep_alive
import random
import requests
from googletrans import Translator
from config import DISCORD_TOKEN, OPEN_CAGE_GEOCODING

intents = discord.Intents.default()
intents.messages = True
intents.dm_messages = True  # Wichtig für DMs

bot = commands.Bot(command_prefix="!", intents=intents)


### Bot startet und meldet sich bereit ###
@bot.event
async def on_ready():
  print(f'✅ {bot.user} ist online und bereit!')


### Nur auf DMs reagieren, nicht auf Server ###
@bot.event
async def on_message(message):
  if message.guild is None and message.author != bot.user:  # Nur DMs erlauben
    await bot.process_commands(message)

### Erinnerungen speichern ###
notizen = {}

@bot.command()
async def merke(ctx, *, text):
    if ctx.author.id not in notizen:
        notizen[ctx.author.id] = []
    notizen[ctx.author.id].append(text)
    await ctx.author.send(f"✅ Deine Notiz wurde gespeichert: {text}")

@bot.command()
async def erinnerung(ctx):
    if ctx.author.id in notizen and notizen[ctx.author.id]:
        liste = "\n".join([f"{idx + 1}. {note}" for idx, note in enumerate(notizen[ctx.author.id])])
        await ctx.author.send(f"📝 Deine Notizen:\n{liste}")
    else:
        await ctx.author.send("❌ Du hast noch keine Notizen gespeichert!")

@bot.command()
async def lösche(ctx, index: int):
    if ctx.author.id in notizen and 0 < index <= len(notizen[ctx.author.id]):
        gelöscht = notizen[ctx.author.id].pop(index - 1)
        await ctx.author.send(f"🗑️ Notiz gelöscht: {gelöscht}")
    else:
        await ctx.author.send("❌ Ungültige Notiznummer!")

@bot.command()
async def würfel(ctx):
  await ctx.author.send(f"🎲 Du hast eine {random.randint(1, 6)} geworfen!")

@bot.command()
async def münze(ctx):
  await ctx.author.send(f"🪙 {random.choice(['Kopf', 'Zahl'])}")

def get_coordinates(stadt: str):
  geocode_url = f"https://api.opencagedata.com/geocode/v1/json?q={stadt}&key={OPEN_CAGE_GEOCODING}"
  response = requests.get(geocode_url)
  data = response.json()

  if response.status_code == 200 and len(data['results']) > 0:
      lat = data['results'][0]['geometry']['lat']
      lon = data['results'][0]['geometry']['lng']
      return lat, lon
  else:
      return None, None

# Wetter abrufen mit Open-Meteo
@bot.command()
async def wetter(ctx, *, stadt: str):
    lat, lon = get_coordinates(stadt)

    if lat is None or lon is None:
        await ctx.author.send("❌ Die Stadt konnte nicht gefunden werden.")
        return

    # Open-Meteo API URL
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&timezone=Europe/Berlin"

    # Anfrage an die API senden
    response = requests.get(url)

    if response.status_code == 200:
        daten = response.json()
        temperatur = daten["current_weather"]["temperature"]
        windspeed = daten["current_weather"]["windspeed"]
        wettercode = daten["current_weather"]["weathercode"]

        # Wetterbeschreibung basierend auf Wettercode
        wetter_dict = {
            0: "☀️ Klarer Himmel",
            1: "🌤️ Überwiegend klar",
            2: "⛅ Teilweise bewölkt",
            3: "☁️ Bewölkt",
            45: "🌫️ Nebel",
            48: "🌫️ Gefrierender Nebel",
            51: "🌦️ Leichter Nieselregen",
            53: "🌦️ Mäßiger Nieselregen",
            55: "🌧️ Starker Nieselregen",
            61: "🌧️ Leichter Regen",
            63: "🌧️ Mäßiger Regen",
            65: "🌧️ Starker Regen",
            80: "🌦️ Leichte Regenschauer",
            81: "🌦️ Mäßige Regenschauer",
            82: "🌧️ Starke Regenschauer",
            95: "⛈️ Gewitter",
            96: "⛈️ Gewitter mit leichtem Hagel",
            99: "⛈️ Gewitter mit starkem Hagel"
        }
        wetter_beschreibung = wetter_dict.get(wettercode, "Unbekanntes Wetter")

        # Wetter-Nachricht senden
        await ctx.author.send(f"🌡️ Temperatur in {stadt}: {temperatur}°C\n"
                              f"💨 Windgeschwindigkeit: {windspeed} km/h\n"
                              f"{wetter_beschreibung}")
    else:
        await ctx.author.send("❌ Fehler beim Abrufen des Wetters.")

@bot.command()
async def umrechnung(ctx, betrag: float, von: str, nach: str):
    url = f"https://api.exchangerate-api.com/v4/latest/{von.upper()}"
    response = requests.get(url).json()

    if nach.upper() in response["rates"]:
        rate = response["rates"][nach.upper()]
        umgerechnet = betrag * rate
        await ctx.author.send(f"{betrag} {von.upper()} = {umgerechnet:.2f} {nach.upper()}")
    else:
        await ctx.author.send("❌ Ungültige Währung!")

@bot.command()
async def übersetze(ctx, sprache: str, *, text: str):
    translator = Translator()
    translation = translator.translate(text, dest=sprache)  

    await ctx.author.send(f"Übersetzung: {translation.text}")

keep_alive()

bot.run(DISCORD_TOKEN)




