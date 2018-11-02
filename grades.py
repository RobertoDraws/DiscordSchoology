import asyncio
import logging
import os
import random
import subprocess
import time
from collections import Counter, defaultdict, namedtuple
from datetime import datetime
from itertools import cycle
from time import localtime, strftime
from urllib.parse import quote

import chalk
import discord
import requests
import schoolopy
import ts
import yaml
from discord.ext import commands
from discord.ext.commands import Bot
from pyshorteners import Shortener

from cogs.utils.chat_formatting import box
from cogs.utils.dataIO import dataIO

DEFAULTS = {"KEY"             : None,
            "SECRET"          : None}

GradeLine = namedtuple("GradeLine", "schoology")


dark = "https://darktv.xyz/wp-content/uploads/2018/05/Untitled-3-4inverted-1.gif"
dark_alt = "https://darktv.xyz/wp-content/uploads/2018/05/May.gif"

class schoologay:
    def __init__(self, bot):
        self.bot = bot
        self.schoology_sessions = []
        self.file_path = "data/schoology/settings.json"
        settings = dataIO.load_json(self.file_path)
        self.settings = defaultdict(lambda: DEFAULTS.copy(), settings)

    @commands.group(pass_context=True, no_pm=False, aliases=["gs", "set"])
    async def gradeset(self, ctx):
        user = ctx.message.author
        settings = self.settings[user.id]
        if ctx.invoked_subcommand is None and ctx.message.channel.is_private:
            print ("{} has used the gradeset command in dms".format(ctx.message.author.name))
            msg = box("Key: {KEY}\n"
                        "Secret: {SECRET}\n"
                        "".format(**settings))
            msg += "\nSee {}help gradeset to edit the settings".format(ctx.prefix)
            await self.bot.say(msg)
        else:
            if not ctx.message.channel.is_private and not ctx.invoked_subcommand:
                print ("{0} has used the gradeset command in {1}".format(ctx.message.author.name, ctx.message.server.name))
                await self.bot.say('This is a public channel. **Please DM me.**')

    def save_settings(self):
        dataIO.save_json(self.file_path, self.settings)

    @gradeset.command(pass_context=True, aliases=["k"])
    async def key(self, ctx, key):
        if ctx.message.channel.is_private:
            print ("{} has used the gradeset key command in dms".format(ctx.message.author.name))
            user = ctx.message.author
            self.settings[user.id]["KEY"] = key
            self.save_settings()
            await self.bot.say("Consumer Key set to {}".format(key))
        else:
            if not ctx.message.channel.is_private:
                print ("{0} has used the gradeset key command in {1}".format(ctx.message.author.name, ctx.message.server.name))
                await self.bot.delete_message(ctx.message)
                await self.bot.say('This is a public channel. **Please DM me.**')

    @gradeset.command(pass_context=True, aliases=["s"])
    async def secret(self, ctx, secret):
        if ctx.message.channel.is_private:
            print ("{} has used the gradeset secret command in dms".format(ctx.message.author.name))
            user = ctx.message.author
            self.settings[user.id]["SECRET"] = secret
            self.save_settings()
            await self.bot.say("Consumer Secret set to {}".format(secret))
        else:
            if not ctx.message.channel.is_private:
                print ("{0} has used the gradeset secret command in {1}".format(ctx.message.author.name, ctx.message.server.name))
                await self.bot.delete_message(ctx.message)
                await self.bot.say('This is a public channel. **Please DM me.**')

    @gradeset.command(pass_context=True, aliases=["r"])
    async def reset(self, ctx):
        if ctx.message.channel.is_private:
            print ("{} has used the gradeset reset command in dms".format(ctx.message.author.name))
            user = ctx.message.author
            self.settings[user.id] = DEFAULTS
            self.save_settings()
            await self.bot.say("Schoology Settings set to default")
        else:
            if not ctx.message.channel.is_private:
                print ("{0} has used the gradeset reset command in {1}".format(ctx.message.author.name, ctx.message.server.name))
                await self.bot.say('This is a public channel. **Please DM me.**')

#    @commands.command(pass_context=True) #Without Section Details
#    async def grades(self, ctx):
#        user = ctx.message.author
#        sc = schoolopy.Schoology(schoolopy.Auth(self.settings[user.id]["KEY"], self.settings[user.id]["SECRET"]))
#        sc.limit = 10  # Only retrieve 10 objects max
#        data = sc.get_user_grades(sc.get_me().uid)
#        embed=discord.Embed(title="",  description="**School:** {0}\n**Grad Year:** {1}".format(sc.get_school(sc.get_me().building_id).title, sc.get_me().grad_year), color=123123, timestamp=datetime.utcnow())
#        embed.set_author(name="{}'s Info".format(sc.get_me().name_display), icon_url=dark_alt)
#        embed.add_field(name='{0} {1}'.format(sc.get_section(data[0]["section_id"]).course_title, sc.get_section(data[7]["section_id"]).section_title), value="**Final:** {0}\n**Minor:** {1}\n**Major:** {2}\n**Practice:** {3}".format(data[0]['final_grade'][0]['grade'], data[0]['final_grade'][0]['grading_category'][0]['grade'], data[0]['final_grade'][0]['grading_category'][1]['grade'], data[0]['final_grade'][0]['grading_category'][2]['grade']), inline=False)
#        embed.add_field(name='{0} {1}'.format(sc.get_section(data[1]["section_id"]).course_title, sc.get_section(data[7]["section_id"]).section_title), value="**Final:** {0}\n**Minor:** {1}\n**Major:** {2}\n**Practice:** {3}".format(data[1]['final_grade'][0]['grade'], data[1]['final_grade'][0]['grading_category'][0]['grade'], data[1]['final_grade'][0]['grading_category'][1]['grade'], data[1]['final_grade'][0]['grading_category'][2]['grade']), inline=False)
#        embed.add_field(name='{0} {1}'.format(sc.get_section(data[2]["section_id"]).course_title, sc.get_section(data[7]["section_id"]).section_title), value="**Final:** {0}\n**Minor:** {1}\n**Major:** {2}\n**Practice:** {3}".format(data[2]['final_grade'][0]['grade'], data[2]['final_grade'][0]['grading_category'][0]['grade'], data[2]['final_grade'][0]['grading_category'][1]['grade'], data[2]['final_grade'][0]['grading_category'][2]['grade']), inline=False)
#        embed.add_field(name='{0} {1}'.format(sc.get_section(data[3]["section_id"]).course_title, sc.get_section(data[7]["section_id"]).section_title), value="**Final:** {0}\n**Minor:** {1}\n**Major:** {2}\n**Practice:** {3}".format(data[3]['final_grade'][0]['grade'], data[3]['final_grade'][0]['grading_category'][0]['grade'], data[3]['final_grade'][0]['grading_category'][1]['grade'], data[3]['final_grade'][0]['grading_category'][2]['grade']), inline=False)
#        embed.add_field(name='{0} {1}'.format(sc.get_section(data[4]["section_id"]).course_title, sc.get_section(data[7]["section_id"]).section_title), value="**Final:** {0}\n**Minor:** {1}\n**Major:** {2}\n**Practice:** {3}".format(data[4]['final_grade'][0]['grade'], data[4]['final_grade'][0]['grading_category'][0]['grade'], data[4]['final_grade'][0]['grading_category'][1]['grade'], data[4]['final_grade'][0]['grading_category'][2]['grade']), inline=False)
#        embed.add_field(name='{0} {1}'.format(sc.get_section(data[5]["section_id"]).course_title, sc.get_section(data[7]["section_id"]).section_title), value="**Final:** {0}\n**Minor:** {1}\n**Major:** {2}\n**Practice:** {3}".format(data[5]['final_grade'][0]['grade'], data[5]['final_grade'][0]['grading_category'][0]['grade'], data[5]['final_grade'][0]['grading_category'][1]['grade'], data[5]['final_grade'][0]['grading_category'][2]['grade']), inline=False)
#        embed.add_field(name='{0} {1}'.format(sc.get_section(data[6]["section_id"]).course_title, sc.get_section(data[7]["section_id"]).section_title), value="**Final:** {0}\n**Minor:** {1}\n**Major:** {2}\n**Practice:** {3}".format(data[6]['final_grade'][0]['grade'], data[6]['final_grade'][0]['grading_category'][0]['grade'], data[6]['final_grade'][0]['grading_category'][1]['grade'], data[6]['final_grade'][0]['grading_category'][2]['grade']), inline=False)
#        embed.add_field(name='{0} {1}'.format(sc.get_section(data[7]["section_id"]).course_title, sc.get_section(data[7]["section_id"]).section_title), value="**Final:** {0}\n**Minor:** {1}\n**Major:** {2}\n**Practice:** {3}".format(data[7]['final_grade'][0]['grade'], data[7]['final_grade'][0]['grading_category'][0]['grade'], data[7]['final_grade'][0]['grading_category'][1]['grade'], data[7]['final_grade'][0]['grading_category'][2]['grade']), inline=False)
#        embed.set_thumbnail(url='{}'.format(sc.get_me().picture_url))
#        embed.set_footer(text='+grades', icon_url=dark)
#        await self.bot.say(embed=embed)

    @commands.command(pass_context=True, no_pm=False) # With Section Details
    async def grades(self, ctx):
        if ctx.message.channel.is_private:
            print ("{} has used the grades command in dms".format(ctx.message.author.name))
            user = ctx.message.author
            sc = schoolopy.Schoology(schoolopy.Auth(self.settings[user.id]["KEY"], self.settings[user.id]["SECRET"]))
            sc.limit = 10  # Only retrieve 10 objects max
            data = sc.get_user_grades(sc.get_me().uid)
            embed=discord.Embed(title="",  description="**School:** {0}\n**Grad Year:** {1}".format(sc.get_school(sc.get_me().building_id).title, sc.get_me().grad_year), color=123123, timestamp=datetime.utcnow())
            embed.set_author(name="{}'s Info".format(sc.get_me().name_display), icon_url=dark_alt)
            embed.add_field(name='{}'.format(sc.get_section(data[0]["section_id"]).course_title), value="**Final:** {0}\n**Minor:** {1}\n**Major:** {2}\n**Practice:** {3}".format(data[0]['final_grade'][0]['grade'], data[0]['final_grade'][0]['grading_category'][0]['grade'], data[0]['final_grade'][0]['grading_category'][1]['grade'], data[0]['final_grade'][0]['grading_category'][2]['grade']), inline=False)
            embed.add_field(name='{}'.format(sc.get_section(data[1]["section_id"]).course_title), value="**Final:** {0}\n**Minor:** {1}\n**Major:** {2}\n**Practice:** {3}".format(data[1]['final_grade'][0]['grade'], data[1]['final_grade'][0]['grading_category'][0]['grade'], data[1]['final_grade'][0]['grading_category'][1]['grade'], data[1]['final_grade'][0]['grading_category'][2]['grade']), inline=False)
            embed.add_field(name='{}'.format(sc.get_section(data[2]["section_id"]).course_title), value="**Final:** {0}\n**Minor:** {1}\n**Major:** {2}\n**Practice:** {3}".format(data[2]['final_grade'][0]['grade'], data[2]['final_grade'][0]['grading_category'][0]['grade'], data[2]['final_grade'][0]['grading_category'][1]['grade'], data[2]['final_grade'][0]['grading_category'][2]['grade']), inline=False)
            embed.add_field(name='{}'.format(sc.get_section(data[3]["section_id"]).course_title), value="**Final:** {0}\n**Minor:** {1}\n**Major:** {2}\n**Practice:** {3}".format(data[3]['final_grade'][0]['grade'], data[3]['final_grade'][0]['grading_category'][0]['grade'], data[3]['final_grade'][0]['grading_category'][1]['grade'], data[3]['final_grade'][0]['grading_category'][2]['grade']), inline=False)
            embed.add_field(name='{}'.format(sc.get_section(data[4]["section_id"]).course_title), value="**Final:** {0}\n**Minor:** {1}\n**Major:** {2}\n**Practice:** {3}".format(data[4]['final_grade'][0]['grade'], data[4]['final_grade'][0]['grading_category'][0]['grade'], data[4]['final_grade'][0]['grading_category'][1]['grade'], data[4]['final_grade'][0]['grading_category'][2]['grade']), inline=False)
            embed.add_field(name='{}'.format(sc.get_section(data[5]["section_id"]).course_title), value="**Final:** {0}\n**Minor:** {1}\n**Major:** {2}\n**Practice:** {3}".format(data[5]['final_grade'][0]['grade'], data[5]['final_grade'][0]['grading_category'][0]['grade'], data[5]['final_grade'][0]['grading_category'][1]['grade'], data[5]['final_grade'][0]['grading_category'][2]['grade']), inline=False)
            embed.add_field(name='{}'.format(sc.get_section(data[6]["section_id"]).course_title), value="**Final:** {0}\n**Minor:** {1}\n**Major:** {2}\n**Practice:** {3}".format(data[6]['final_grade'][0]['grade'], data[6]['final_grade'][0]['grading_category'][0]['grade'], data[6]['final_grade'][0]['grading_category'][1]['grade'], data[6]['final_grade'][0]['grading_category'][2]['grade']), inline=False)
            embed.add_field(name='{}'.format(sc.get_section(data[7]["section_id"]).course_title), value="**Final:** {0}\n**Minor:** {1}\n**Major:** {2}\n**Practice:** {3}".format(data[7]['final_grade'][0]['grade'], data[7]['final_grade'][0]['grading_category'][0]['grade'], data[7]['final_grade'][0]['grading_category'][1]['grade'], data[7]['final_grade'][0]['grading_category'][2]['grade']), inline=False)
            embed.set_thumbnail(url='{}'.format(sc.get_me().picture_url))
            embed.set_footer(text='+grades', icon_url=dark)
            await self.bot.say(embed=embed)
        else:
            if not ctx.message.channel.is_private:
                print ("{0} has used the grades command in {1}".format(ctx.message.author.name, ctx.message.server.name))
                await self.bot.delete_message(ctx.message)
                await self.bot.say('This is a public channel. **Please DM me.**')
    
def check_folders():
    folders = ("data", "data/schoology/")
    for folder in folders:
        if not os.path.exists(folder):
            print("Creating " + folder + " folder...")
            os.makedirs(folder)

def check_files():
    if not os.path.isfile("data/schoology/settings.json"):
        print("Creating empty settings.json...")
        dataIO.save_json("data/schoology/settings.json", {})

def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(schoologay(bot))
