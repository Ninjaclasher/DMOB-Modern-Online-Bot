from .BaseHandler import BaseHandler
from discord import *
from util import *

import database

async def get_user_id(self, info):
    if len(info['message'].mentions) != 1:
        await info['bot'].send_message(info['channel'], "Please mention one user in the message.")
        return None
    return info['message'].mentions[0].id


class User(BaseHandler):
    async def list(self, info):
        user_list = [x for x in database.users.values() if x.points > 0]
        user_list.sort(key=lambda x: [-x.points, str(x)])    
        current_list, page_num = await get_current_list(info, user_list, 30)
        if current_list is None:
            return
        em = Embed(title="Users", description="Users page {}".format(page_num), color=BOT_COLOUR)
        if len(user_list) == 0:
            em.add_field(name="No users", value="No users have any points.")
        else:
            em.add_field(name="Rank", value = "\n".join(map(str, range(1, len(current_list)+1))))
            em.add_field(name="User", value = "\n".join(x.discord_user.mention for x in current_list))
            em.add_field(name="Points", value = "\n".join(str(x.points) for x in current_list))
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
