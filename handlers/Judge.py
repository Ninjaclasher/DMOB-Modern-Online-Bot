from .BaseHandler import BaseHandler
from discord import *
from util import *
import database
import models
import multiprocessing
import os
import sys

def run_judge(judge_name):
    sys.argv = ["python -m dmoj"] + "-p {1} -c judges/{2}.yml {0}".format(*BRIDGED_IP_ADDRESS[0], judge_name).split(" ")
    sys.stderr = open("judges/{}.log".format(judge_name), "a")
    sys.stdout = sys.stderr
    import dmoj.judge
    dmoj.judge.main()

def get_judge(judge_name):
    try:
        return database.get_judges(name=judge_name)[0]
    except IndexError:
        return None

class Judge(BaseHandler):
    async def list(self, info):
        online_judges = [x.name for x in database.judgeserver.judges.judges]
        offline_judges = [x for x in database.get_judges() if x.name not in online_judges] if info['user'].is_admin else []
        judge_name = ["✓ {}".format(x) for x in online_judges] + [x.name for x in offline_judges]
        judge_ping = [str(round(x.latency,3)) if x.latency is not None else "N/A" for x in database.judgeserver.judges.judges] + ["N/A"]*len(offline_judges)
        judge_load = [str(round(x.load, 3)) if x.load < 1e10 else "N/A" for x in database.judgeserver.judges.judges] + ["N/A"]*len(offline_judges)
        
        em = Embed(title="Judges", description="List of judges.")
        if len(judge_name) == 0:
            em.add_field(name="No Judges", value="There are no judges.")
        else:
            em.add_field(name="Judge Name", value="\n".join(judge_name))
            em.add_field(name="Ping", value="\n".join(judge_ping))
            em.add_field(name="Load", value="\n".join(judge_load))
        await info['bot'].send_message(info['channel'], embed=em)
    
    async def view(self, info):
        online_judges = [x.name for x in database.judgeserver.judges.judges]
        try:
            judge_name = info['content'][0]
        except IndexError:
            await info['bot'].send_message(info['channel'], "Please enter a judge name.")
            return
        with await database.locks["judge"][judge_name]:
            if get_judge(judge_name) is None:
                await info['bot'].send_message(info['channel'], "Judge with name `{}` does not exist.".format(info['content'][0]))
                return
            em = Embed(title="Judge Info", description="{} Details".format(judge_name), color=BOT_COLOUR)
            fields = {
                    "Judge Name": ("✓ " if judge_name in online_judges else "") + judge_name.capitalize(),
                    "Ping"      : "N/A",
                    "Load"      : "N/A",
                    "Supported Languages" : "N/A",
            }
            if judge_name in online_judges:
                for x in database.judgeserver.judges.judges:
                    if x.name == judge_name:
                        fields["Ping"] = round(x.latency, 3) if x.latency is not None else "----"
                        fields["Load"] = round(x.load, 3) if x.load < 1e10 else "----"
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
            if get_judge(judge_name) is not None:
                await info['bot'].send_message(info['channel'], "Judge with name `{}` already exists.".format(judge_name))
                return
            database.add_judge(models.Judge(None, judge_name, judge_key))
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
            judge = get_judge(judge_name)
            if judge is None:
                await info['bot'].send_message(info['channel'], "Judge with name `{}` does not exist.".format(judge_name))
                return
            database.delete_judge(judge)
            await info['bot'].send_message(info['channel'], "Judge `{}` successfully deleted!".format(judge_name))

    async def start(self, info):
        if not await has_perm(info['bot'], info['channel'], info['user'], "start judges"):
            return
        try:
            judge_name = info['content'][0]
            if get_judge(judge_name) is None:
                raise IndexError
        except IndexError:
            await info['bot'].send_message(info['channel'], "Please enter a valid judge name.")
            return
        
        with await database.locks["judge"][judge_name]:
            if judge_name in database.judges.keys():
                await info['bot'].send_message(info['channel'], "Judge `{}` is already running.".format(judge_name))
                return
            database.judges[judge_name] = multiprocessing.Process(target=run_judge, args=(judge_name,))
            database.judges[judge_name].start()
            await info['bot'].send_message(info['channel'], "Judge `{}` has been started".format(judge_name))

    async def stop(self, info):
        if not await has_perm(info['bot'], info['channel'], info['user'], "stop judges"):
            return
        try:
            judge_name = info['content'][0]
            if get_judge(judge_name) is None:
                raise IndexError
            elif judge_name not in database.judges.keys():
                raise KeyError
        except IndexError:
            await info['bot'].send_message(info['channel'], "Please enter a valid judge name.")
            return
        except KeyError:
            await info['bot'].send_message(info['channel'], "Judge `{}` is not running.".format(judge_name))
            return
        
        with await database.locks["judge"][judge_name]:
            database.judges[judge_name].terminate()
            del database.judges[judge_name]
            await info['bot'].send_message(info['channel'], "Judge `{}` has been forcefully stopped.".format(judge_name))

