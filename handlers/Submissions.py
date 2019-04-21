from .BaseHandler import BaseHandler
from discord import *
from util import *
import database


async def get_submission(self, info):
    try:
        return database.get_submissions(id=int(info['content'][0]))[0]
    except (KeyError, IndexError):
        await info['bot'].send_message(info['channel'], "Please enter a valid submission id.")
    return None


def batched(cases):
    ret = {}
    for x in cases:
        try:
            ret[x.batch].append(x)
        except KeyError:
            ret[x.batch] = [x]
    return [list(x) for x in ret.values() if len(x) > 0]


class Submissions(BaseHandler):
    async def list(self, info):
        current_list, page_num = await get_current_list(info, database.get_submissions())
        if current_list is None:
            return
        em = Embed(title="Submissions", description="Submission page {}".format(page_num), color=BOT_COLOUR)
        for x in current_list:
            value = """\
By: {0}
Problem: {1}
Score: {2}/{3}
Verdict: {4}
            """.format(x.user.discord_user, x._problem, x.points, x.total, x.result)
            em.add_field(name="Submission #{}".format(x.submission_id), value=value)
        await info['bot'].send_message(info['channel'], embed=em)

    async def view(self, info, live_submission=False, submission=None):
        sub = await get_submission(self, info) if submission is None else submission
        if sub is None:
            return
        with await database.locks["submissions"][sub.submission_id]:
            if live_submission:
                description = "Details on your submission to `{}`".format(sub.problem.code)
            else:
                description = "Details on submission #{}".format(sub.submission_id)
            em = Embed(title="Submission Details", description=description, color=sub.verdict_colour)
            em.add_field(name="Problem Name", value=sub.problem.name)
            em.add_field(name="Submission ID", value=str(sub.submission_id))
            em.add_field(name="Submission Time", value=to_datetime(sub.submission_time))
            em.add_field(name="Verdict", value="{0} ({1})".format(sub.result, sub.verdict_full))
            if sub.result == "QU":
                em.add_field(name="Points Recieved", value="???")
                em.add_field(name="Total Running Time", value="???")
                em.add_field(name="Memory Usage", value="???")
            else:
                em.add_field(name="Points Recieved", value="{0}/{1}".format(sub.points, float(sub.total)))
                em.add_field(name="Total Running Time", value="{}s".format(round(sub.time, 4)))
                em.add_field(name="Memory Usage", value=to_memory(sub.memory))
            await info['bot'].send_message(info['channel'], embed=em)
            if sub.result == "QU" or not await has_perm(info['bot'], info['channel'], info['user'],
                                                        "view submission #{}".format(sub.submission_id), not sub.is_by(info['user']), False):
                return
            num_per_embed = 20
            embeds = []
            for x in batched(database.get_submission_cases(sub.submission_id)):
                values = ["`Case #{0: >3}: {1: >3}{2}`".format(i, y.status if y.status != "SC" else "--",
                          "{0: >8}s, {1: >8}]".format("[{:.3f}".format(round(y.time, 3)), to_memory(y.memory)) if y.status != "SC" else "") for i, y in enumerate(x, 1)]
                name = "Batch #{}".format(x[0].batch) if x[0].batch != -1 else "Test Cases"
                if len(values) > num_per_embed:
                    chunked = [values[x:x + num_per_embed] for x in range(0, len(values), num_per_embed)]
                    for i, y in enumerate(chunked, 1):
                        em = Embed(title="Submission Cases", description=description, color=sub.verdict_colour)
                        em.add_field(name="{0} Part {1}".format(name, i), value="\n".join(y))
                        embeds.append(em)
                else:
                    em = Embed(title="Submission Cases", description=description, color=sub.verdict_colour)
                    em.add_field(name=name, value="\n".join(values))
                    embeds.append(em)
            with await database.locks["user"][info['user'].id]:
                for x in embeds:
                    await info['bot'].send_message(info['user'].discord_user, embed=x)

    async def code(self, info):
        sub = await get_submission(self, info)
        if sub is None:
            return
        with await database.locks["submissions"][sub.submission_id]:
            if not await has_perm(info['bot'], info['channel'], info['user'], "view submission #{}".format(sub.submission_id), not sub.is_by(info['user'])):
                return
            await info['bot'].send_message(info['user'].discord_user, "Code preview:\n```\n{}\n```\n".format(sub.source[:1900]))
            with open("/tmp/{}.code".format(sub.submission_id), "w") as s:
                s.write(sub.source)
            await info['bot'].send_file(info['user'].discord_user, "/tmp/{}.code".format(sub.submission_id))
            await info['bot'].send_message(info['channel'], "{} The code has been sent to your private messages.".format(info['user'].discord_user.mention))

    async def delete(self, info):
        sub = await get_submission(self, info)
        if sub is None:
            return
        with await database.locks["submissions"][sub.submission_id]:
            if not await has_perm(info['bot'], info['channel'], info['user'], "delete submission #{}".format(sub.submission_id)):
                return
            database.delete_submission(sub)
            await sub.user.update_points()
            await info['bot'].send_message(info['channel'], "Successfully deleted submission #{}".format(sub.submission_id))
