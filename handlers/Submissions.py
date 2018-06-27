from discord import *
from util import *
import database
import models
import os

async def get_submission(info):
    try:
        sub = get_element(database.submission_list, models.Submission(int(info['content'][0])))
        if sub is None:
            raise KeyError
        return sub
    except (ValueError, KeyError):
        await info['bot'].send_message(info['channel'], "Please enter a valid submission id.")
        return None
    except IndexError:
        await info['bot'].send_message(info['channel'], "Please enter a submission id.")
        return None

class Submissions:
    @staticmethod
    async def help(info):
        em = Embed(title="Submissions Help",description="Available Submissions commands from DMOB", color=BOT_COLOUR)
        for key, value in help_list["submissions"].items():
            em.add_field(name=COMMAND_PREFIX + "submissions " + key, value=value)
        await info['bot'].send_message(info['channel'], embed=em)

    @staticmethod
    async def list(info):
        try:
            page_num = int(info['content'][0]) if len(info['content']) > 0 else 1
            elements_per_page = 9
            if page_num < 1 or (page_num-1)*elements_per_page > len(database.submission_list):
                raise ValueError
            em = Embed(title="Submissions",description="Submission page " + str(page_num), color=BOT_COLOUR)
            for x in database.submission_list[(page_num-1)*elements_per_page : min(page_num*elements_per_page, len(database.submission_list))]:
                values = ["By: " + str(x.user.discord_user), "Problem: " + str(x.problem.problem_name), "Score: " + str(x.points) + "/" + str(x.total), "Verdict: " + x.result]
                em.add_field(name="Submission #" + str(x.submission_id), value='\n'.join(values))
            await info['bot'].send_message(info['channel'], embed=em)
        except (ValueError, IndexError):
            await info['bot'].send_message(info['channel'], "Please enter a valid page number.")

    @staticmethod
    async def view(info):
        sub = await get_submission(info)
        if sub is None:
            return
        with await database.locks["submissions"][sub.submission_id]:
            try:
                description = info['description']
            except KeyError:
                description = "Details on submission #" + info['content'][0]
            em = Embed(title="Submission Details", description=description, color=verdict_colours[sub.result])
            em.add_field(name="Problem Name", value=sub.problem.problem_name)
            em.add_field(name="Submission ID", value=str(sub.submission_id))
            em.add_field(name="Submission Time", value=to_datetime(sub.submission_time))
            em.add_field(name="Verdict", value=sub.result + " (" + verdicts[sub.result] + ")")
            em.add_field(name="Points Recieved", value=str(sub.points) + "/" + str(float(sub.total)))
            em.add_field(name="Total Running Time", value=str(round(sub.time,4)) + "s")
            em.add_field(name="Memory Usage", value=to_memory(sub.memory))
            await info['bot'].send_message(info['channel'], embed=em)

    @staticmethod
    async def code(info):
        sub = await get_submission(info)
        if sub is None:
            return
        with await database.locks["submissions"][sub.submission_id]:
            if not await has_perm(info['bot'], info['channel'], info['user'], "view submission #" + str(sub.submission_id), not sub.is_by(info['user'])):
                return
            await info['bot'].send_message(info['user'].discord_user, "Code preview:\n```\n" + sub.source[:1900] + "\n```\n")
            await info['bot'].send_file(info['user'].discord_user, "submissions/" + str(sub.submission_id) + ".code")
            await info['bot'].send_message(info['channel'], info['user'].discord_user.mention + " The code has been sent to your private messages.")

    @staticmethod
    async def delete(info):
        sub = await get_submission(info)
        if sub is None:
            return
        with await database.locks["submissions"][sub.submission_id]:
            if not await has_perm(info['bot'], info['channel'], info['user'], "delete submission #" + str(sub.submission_id)):
                return
            database.submission_list.remove(sub)
            os.system("mv submissions/" + str(sub.submission_id) + ".* deleted_submissions/")
            await info['bot'].send_message(info['channel'], "Successfully deleted submission #" + str(sub.submission_id))
