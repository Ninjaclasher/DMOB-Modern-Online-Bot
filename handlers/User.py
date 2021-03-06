import os

from .BaseHandler import BaseHandler
from discord import *
from util import *
import database


async def get_user_id(self, info, error_message=True):
    if len(info['message'].mentions) != 1:
        if error_message:
            await info['bot'].send_message(info['channel'], "Please mention one user in the message.")
        return None
    return info['message'].mentions[0].id


class User(BaseHandler):
    async def list(self, info):
        user_list = [x for x in database.users.values()]
        user_list.sort(key=lambda x: [-x.rating if x.rated else 0, str(x)])
        current_list, page_num = await get_current_list(info, user_list, 30)
        if current_list is None:
            return
        em = Embed(title="Users", description="Users page {}".format(page_num), color=BOT_COLOUR)
        if len(user_list) == 0:
            em.add_field(name="No users", value="There are no users that have a rating.")
        else:
            em.add_field(name="Rank", value="\n".join(map(str, range(1, len(current_list) + 1))))
            em.add_field(name="User", value="\n".join("{0} {1}".format(x.discord_user.mention, "[Admin]" if x.is_admin else "") for x in current_list))
            em.add_field(name="Rating", value="\n".join(str(x.rating) if x.rated else "----" for x in current_list))
        await info['bot'].send_message(info['channel'], embed=em)

    async def view(self, info):
        id = await get_user_id(self, info, False)
        user = info['user'] if id is None else await database.load_user(info['bot'], id)
        em = Embed(title="User Details", description="{} Details".format(user.discord_user), colour=user.rank_colour)
        em.add_field(name="User", value="{0} {1}".format(user.discord_user.mention, "[Admin]" if user.is_admin else ""))
        em.add_field(name="Points", value="{}p".format(user.points))
        em.add_field(name="Current Language", value="{}".format(user.language))
        em.add_field(name="Rating Title", value="{}".format(user.rank_title))
        if user.rated:
            em.add_field(name="Rating Points", value="{}".format(user.rating))
            em.add_field(name="Volatility", value="{}".format(user.volatility))
        await info['bot'].send_message(info['channel'], embed=em)

    async def submissions(self, info):
        id = await get_user_id(self, info, False)
        if id is not None:
            del info['content'][0]
        user = info['user'] if id is None else await database.load_user(info['bot'], id)
        current_list, page_num = await get_current_list(info, user.submissions)
        if current_list is None:
            return
        em = Embed(title="User Submissions", description="User Submissions page {}".format(page_num), color=BOT_COLOUR)
        if len(current_list) == 0:
            em.add_field(name="No Submissions", value="{} has no submissions.".format(user.discord_user.mention))
        else:
            for x in current_list:
                values = """\
Problem: {0}
Score: {1}/{2}
Verdict: {3}
                """.format(x.problem.name, x.points, x.total, x.result)
                em.add_field(name="Submission #{}".format(x.submission_id), value=values)
        await info['bot'].send_message(info['channel'], embed=em)

    async def make(self, info):
        if not await has_perm(info['bot'], info['channel'], info['user'], "change user properties"):
            return
        id = await get_user_id(self, info)
        if id is None:
            return
        try:
            value = info['content'][0].lower()
            if value not in ["admin", "normal"]:
                raise ValueError
        except (ValueError, IndexError):
            await info['bot'].send_message(info['channel'], "Failed to parse the message content to change the user. Please try again.")
        with await database.locks["user"][id]:
            user = await database.load_user(info['bot'], id)
            if user.is_admin == int(value == "admin"):
                await info['bot'].send_message(info['channel'], "User is already a{0} {1} user.".format("n" if value == "admin" else "", value))
                return
            user.is_admin = int(value == "admin")
            await info['bot'].send_message(info['channel'], "Successfully made user a{0} {1} user.".format("n" if value == "admin" else "", value))

    async def reset(self, info):
        if not await has_perm(info['bot'], info['channel'], info['user'], "reset users"):
            return
        id = await get_user_id(self, info)
        with await database.locks["user"][id]:
            await database.load_user(info['bot'], id)
            if id is None:
                return
            del database.users[id]
            try:
                os.remove("players/{}.json".format(id))
            except FileNotFoundError:
                pass
        await info['bot'].send_message(info['channel'], "Successfully reset {}".format(str(database.discord_users_list[id])))
