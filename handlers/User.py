from .BaseHandler import BaseHandler
from discord import *
from util import *

import database

async def get_user_id(self, info, error_message = True):
    if len(info['message'].mentions) != 1:
        if error_message:
            await info['bot'].send_message(info['channel'], "Please mention one user in the message.")
        return None
    return info['message'].mentions[0].id


class User(BaseHandler):
    async def list(self, info):
        user_list = [x for x in database.users.values() if x.rank > 0]
        user_list.sort(key=lambda x: [-x.rank, str(x)])    
        current_list, page_num = await get_current_list(info, user_list, 30)
        if current_list is None:
            return
        em = Embed(title="Users", description="Users page {}".format(page_num), color=BOT_COLOUR)
        if len(user_list) == 0:
            em.add_field(name="No users", value="There are no users that have a rating.")
        else:
            em.add_field(name="Rank", value = "\n".join(map(str, range(1, len(current_list)+1))))
            em.add_field(name="User", value = "\n".join(x.discord_user.mention for x in current_list))
            em.add_field(name="Rating", value = "\n".join(str(x.rank) for x in current_list))
        await info['bot'].send_message(info['channel'], embed=em)
    
    async def view(self, info):
        id = await get_user_id(self, info, False)
        user = info['user'] if id is None else await database.load_user(info['bot'], id)
        em = Embed(title="User Details", description="{} Details".format(user.discord_user), colour=ranking_colour[user.rank_title])
        em.add_field(name="User", value="{} {}".format(user.discord_user.mention, "(Administrator)" if user.is_admin else ""))
        em.add_field(name="Points", value="{}p".format(user.points))
        em.add_field(name="Current Language", value="{}".format(user.language))
        em.add_field(name="Ranking Points", value="{}".format(user.rank))
        em.add_field(name="Ranking Title", value="{}".format(user.rank_title))
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
        except (KeyError, ValueError, IndexError):
            await info['bot'].send_message(info['channel'], "Failed to parse the message content to change the user. Please try again.")
        with await database.locks["user"][id]:
            user = await database.load_user(info['bot'], id)
            if user.is_admin == int(value == "admin"):
                await info['bot'].send_message(info['channel'], "User is already a{0} {1} user.".format("n" if value == "admin" else "", value))
                return
            user.is_admin = int(value=="admin")
            await info['bot'].send_message(info['channel'], "Successfully made user a{0} {1} user.".format("n" if value == "admin" else "", value))
    
    async def reset(self, info):
        if not await has_perm(info['bot'], info['channel'], info['user'], "reset users"):
            return
        id = await get_user_id(self, info)
        if id is None:
            return
        del database.users[id]
        await info['bot'].send_message(info['channel'], "Successfully reset {}".format(str(database.discord_users_list[id])))
