from .BaseHandler import BaseHandler
from discord import *
from util import *
import database
import models
import os
import threading

class Judge(BaseHandler):
    async def list(self, info):
        online_judges = [x.name for x in database.judgeserver.judges.judges]
        offline_judges = [x for x in database.judge_list if x.id not in online_judges] if info['user'].is_admin else []
        judge_name = ["✓ {}".format(x) for x in online_judges] + [x.id for x in offline_judges]
        judge_ping = [str(round(x.latency,3)) if x.latency is not None else "N/A" for x in database.judgeserver.judges.judges] + ["N/A"]*len(offline_judges)
        judge_load = [str(round(x.load, 3)) if x.latency is not 1e100 else "N/A" for x in database.judgeserver.judges.judges] + ["N/A"]*len(offline_judges)
        
        em = Embed(title="Judges", description="List of judges.")
        em.add_field(name="Judge Name", value="\n".join(judge_name))
        em.add_field(name="Ping", value="\n".join(judge_ping))
        em.add_field(name="Load", value="\n".join(judge_load))
        await info['bot'].send_message(info['channel'], embed=em)
    
    async def view(self, info):
        online_judges = [x.name.lower() for x in database.judgeserver.judges.judges]
        try:
            judge_name = info['content'][0].lower()
        except IndexError:
            await info['bot'].send_message(info['channel'], "Please enter a judge name.")
            return
        with await database.locks["judge"][judge_name]:
            if judge_name not in [x.id.lower() for x in database.judge_list]:
                await info['bot'].send_message(info['channel'], "Judge with name `{}` does not exist.".format(info['content'][0]))
                return
            em = Embed(title="Judge Info", description="{} Details".format(judge_name.capitalize()), color=BOT_COLOUR)
            fields = {
                    "Judge Name": ("✓ " if judge_name in online_judges else "") + judge_name.capitalize(),
                    "Ping"      : "N/A",
                    "Load"      : "N/A",
                    "Supported Languages" : "N/A",
            }
            if judge_name in online_judges:
                for x in database.judgeserver.judges.judges:
                    if x.name.lower() == judge_name:
                        fields["Ping"] = round(x.latency, 3) if x.latency is not None else "N/A"
                        fields["Load"] = round(x.load, 3) if x.load is not 1e100 else "N/A"
                        fields["Supported Languages"] = ", ".join(dmob_lang[y] for y in x.executors.keys() if y in dmob_lang.keys())
                        break
            for x, y in fields.items():
                em.add_field(name=x, value=y)
            await info['bot'].send_message(info['channel'], embed=em)    
    
    async def add(self, info):
        if not await has_perm(info['bot'], info['channel'], info['user'], "add judges"):
            return
        try:
            judge_name = info['content'][0]
            judge_key = info['content'][1]
        except IndexError:
            await info['bot'].send_message(info['channel'], "Could not parse message content and add a judge. Please try again.")
            return
        with await database.locks["judge"][judge_name]:
            await info['bot'].delete_message(info['message'])
            if judge_name.lower() in [x.id.lower() for x in database.judge_list]:
                await info['bot'].send_message(info['channel'], "Judge with name `{}` already exists.".format(judge_name))
                return
            database.judge_list.append(models.Judge(judge_name, judge_key))
            await info['bot'].send_message(info['channel'], "Judge `{}` successfully added!".format(judge_name))

    async def delete(self, info):
        if not await has_perm(info['bot'], info['channel'], info['user'], "delete judges"):
            return
        try:
            judge_name = info['content'][0]
        except IndexError:
            await info['bot'].send_message(info['channel'], "Please enter a valid judge name.")
            return
        with await database.locks["judge"][judge_name]:
            if not judge_name.lower() in [x.id.lower() for x in database.judge_list]:
                await info['bot'].send_message(info['channel'], "Judge with name `{}` does not exist.".format(judge_name))
                return
            for x in range(len(database.judge_list)):
                if database.judge_list[x].id.lower() == judge_name.lower():
                    del database.judge_list[x]
            await info['bot'].send_message(info['channel'], "Judge `{}` successfully deleted!".format(judge_name))

    async def start(self, info):
        if not await has_perm(info['bot'], info['channel'], info['user'], "start judges"):
            return
        try:
            judge_name = info['content'][0]
            if judge_name not in [x.id for x in database.judge_list]:
                raise IndexError
        except IndexError:
            await info['bot'].send_message(info['channel'], "Please enter a valid judge name.")
            return
        
        with await database.locks["judge"][judge_name]:
            if judge_name in [x.name for x in database.judgeserver.judges]:
                await info['bot'].send_message(info['channel'], "Judge `{}` is already running.".format(judge_name))
                return
            threading.Thread(target=os.system, args=("screen -dmS judge bash -c \"dmoj -p {1} -c judges/{2}.yml {0}\"".format(*BRIDGED_IP_ADDRESS[0], judge_name), )).start()
            await info['bot'].send_message(info['channel'], "Judge `{}` has been started".format(judge_name))

    async def stop(self, info):
        if not await has_perm(info['bot'], info['channel'], info['user'], "stop judges"):
            return
        try:
            judge_name = info['content'][0]
            if judge_name not in [x.id for x in database.judge_list]:
                raise IndexError
            elif judge_name not in [x.name for x in database.judgeserver.judges]:
                raise KeyError
        except IndexError:
            await info['bot'].send_message(info['channel'], "Please enter a valid judge name.")
            return
        except KeyError:
            await info['bot'].send_message(info['channel'], "Judge `{}` is not running.".format(judge_name))
            return
        
        with await database.locks["judge"][judge_name]:
            #TODO
            return
            await info['bot'].send_message(info['channel'], "Judge `{}` has been forcefully stopped.".format(judge_name))

