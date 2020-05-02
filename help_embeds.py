import discord


def get_help_german():
    help_embed = discord.Embed(title="Hilfe", colour=discord.Colour.blue())

    help_embed.description = "Für jegliche Befehle muss der Präfix 's?' vorangestellt werden"

    help_embed.add_field(name="help", value="\u200b", inline=True)
    help_embed.add_field(
        name="\u200b", value="Zeigt diese Liste mit Befehlen an\nBsp: s?help", inline=True)

    help_embed.add_field(name="\u200b", value="\u200b", inline=False)

    help_embed.add_field(name="create custom", value="\u200b", inline=True)
    help_embed.add_field(
        name="\u200b", value="Erstellt eine Umfrage mit selbst gewählten Emojis.\nNach Eingabe des Befehls den Anweisungen folgen im Chat folgen", inline=True)

    help_embed.add_field(name="\u200b", value="\u200b", inline=False)

    help_embed.add_field(name="create automatic", value="\u200b", inline=True)
    help_embed.add_field(
        name="\u200b", value="""Erstellt eine Umfrage mit automatischen Emojis.
        Benutzung: s?create automatic title;umf1[;umf2...]

        Bsp: s?create automatic Ueberschrift;umf1;umf2
        Würde eine Umfrage mit dem Titel \"Ueberschrift\" und den Umfrageoptionen \"umf1\", \"umf2\" erstellen.
        Hierbei sollte darauf geachtet werden, dass die Umfrageoptionen mit einem \";\" getrennt werden""", inline=True)

    help_embed.add_field(name="\u200b", value="\u200b", inline=False)

    help_embed.add_field(name="addrole", value="\u200b", inline=True)
    help_embed.add_field(
        name="\u200b", value="""Fügt eine Rolle hinzu, die den Bot bedienen darf.
        Nach Eingabe des Befehls, muss in der Liste die Nummer der Rolle eingegeben werden, die hinzugefügt werden soll.""", inline=True)

    help_embed.add_field(name="\u200b", value="\u200b", inline=False)

    help_embed.add_field(name="addchannel", value="\u200b", inline=True)
    help_embed.add_field(
        name="\u200b", value="""Fügt einen Channel hinzu, indem die Botbefehle ausgeführt werden dürfen.
        Nach Eingabe des Befehls, muss in der Liste die Nummer der Rolle eingegeben werden, die hinzugefügt werden soll""", inline=True)

    return help_embed
