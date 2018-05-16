import time

class DMOBGame:
    def __init__(self, bot, channel):
        self.channel = channel
        self.bot = bot
        self.members = []
        self.contest = None
        self.window = 0
        self.start_time = 0
    async def reset(self):
        self.start_time = 0
        self.window = 0
        self.contest = None
        self.members = []
    async def check_contest_running(self, message="There is no contest running in this channel! Please start a contest first."):
        if self.start_time == 0:
            await self.bot.send_message(self.channel, message)
            return False
        return True
    async def join(self, user):
        if not await self.check_contest_running():
            return
        if user in self.members:
            await self.bot.send_message(self.channel, "You are already in the contest!")
        else:
            self.members.append(user)
            await self.bot.send_message(self.channel, "You have joined the contest!")
    async def submit(self, user, problem_code, code_file):
        pass
    async def start_round(self, contest, window=10800):
        if self.start_time != 0:
            await self.bot.send_message(self.channel, "There is already a game runnning in this channel. Please wait until the contest is over.")
            return
        self.contest = contest
        self.start_time = time.time()
        await self.bot.send_message(self.channel, "A contest has started!")
    async def display_problem(self, user, problem_code):
        if not user in self.members:
            await self.bot.send_message(self.channel, "You are not in this contest! Please join first.")
            return True
        discord_user = await self.bot.get_user_info(user.discord_id)
        for x in self.contest.problems:
            if x.problem_code == problem_code:
                await self.bot.send_file(discord_user, x.file)
                await self.bot.send_message(self.channel, discord_user.mention + ", problem statement has been sent to your private messages.")
                return True
        await self.bot.send_message(self.channel, "```\nThe problems in this contest are:\n" + "\n".join(x.problem_code for x in self.contest.problems) + "\n```")
        return False

    async def rankings(self):
        if not await self.check_contest_running():
            return
        await self.bot.send_message(self.channel, "The current rankings are: ")
        await self.bot.send_message(self.channel, "UNIMPLEMENTED")
    async def end_round(self):
        if not await self.check_contest_running():
            return
        await self.bot.send_message(self.channel, "The contest has been forcefully ended!")
        await self.reset()
        
