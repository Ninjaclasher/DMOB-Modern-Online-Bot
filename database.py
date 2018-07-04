import asyncio
import pymysql
import threading
from collections import defaultdict
from util import *
from settings import *

contest_list = {}
problem_list = {}
discord_users_list = {}
users = {}
games = {}
locks = {}
judge_list = []
judgeserver = None
judges = {}
loading = False
db = None

def sql_format(arr):
    return ", ".join(["%s"]*len(arr))

def db_insert(table, values):
    global db
    with locks["db"]["read"] and locks["db"]["write"]:
        cursor = db.cursor()
        cursor.execute("""\
            INSERT INTO {0} VALUES ({1})
        """.format(table, sql_format(values)), values)
        cursor.close()
        db.commit()
        return cursor.lastrowid

def db_select(table, where_condition="", values=(), extra=""):
    global db
    with locks["db"]["read"]:
        cursor = db.cursor()
        cursor.execute("""\
            SELECT *
            FROM {0}
            {1}
            {2}
        """.format(table, "WHERE " + where_condition if where_condition != "" else "", extra), values
        )
        cursor.close()
        return cursor.fetchall()

def db_delete(table, where_condition="", values=()):
    global db
    with locks["db"]["read"] and locks["db"]["write"]:
        cursor = db.cursor()
        cursor.execute("""\
            DELETE
            FROM {0}
            {1}
        """.format(table, "WHERE " + where_condition if where_condition != "" else ""), values
        )
        cursor.close()
        db.commit()

def add_contest(contest):
    global contest_list
    contest.id = db_insert("dmob_contest", contest.db_save())
    for x in contest._problems:
        db_insert("dmob_contest_problem", (None, contest.id, x))
    contest_list[contest.name] = contest

def delete_contest(contest):
    global contest_list
    db_delete("dmob_contest", "id = %s", (contest.id, ))
    db_delete("dmob_contest_problem", "contest_id = %s", (contest.id, ))
    del contest_list[contest.name]

def add_problem(problem):
    global problem_list
    problem.id = db_insert("dmob_problem", problem.db_save())
    problem_list[problem.code] = problem

def change_problem(problem, field, new_value):
    global problem_list
    global db
    cursor = db.cursor()
    cursor.execute("""\
        UPDATE dmob_problem
        SET {}=%s
        WHERE id = %s
    """.format(field), (new_value, problem.id))
    cursor.close()
    db.commit()
    problem.__dict__[field] = new_value

def delete_problem(problem):
    global problem_list
    db_delete("dmob_problem", "id = %s", (problem.id, ))
    del problem_list[problem.code]

def add_rank(rank):
    db_insert("dmob_user_rating", rank.db_save())

def get_ranks(user):
    tmp = db_select(
        "dmob_user_rating",
        where_condition="user = %s",
        values=(user.id, ),
    )
    from models import Rank
    return [Rank(*x) for x in tmp]

def add_submission(sub):
    global db
    cursor = db.cursor()
    cursor.execute("""\
        UPDATE dmob_submissions
        SET points=%s, total=%s, time=%s, memory=%s, result=%s
        WHERE id = %s
    """, (sub.points, sub.total, sub.time, sub.memory, sub.result, sub.submission_id))
    cursor.close()
    db.commit()

def create_submission(sub):
    return db_insert("dmob_submissions", sub.db_save())

def delete_submission(sub):
    global db
    cursor = db.cursor()
    cursor.execute("""\
        UPDATE dmob_submissions
        SET deleted = 1
        WHERE id = %s
    """, (sub.submission_id, ))
    cursor.close()
    sub.deleted = 1

def get_submission(id):
    tmp = db_select(
        "dmob_submissions",
        where_condition="id = %s AND deleted = 0",
        values = (id,),
    )
    from models import Submission
    try:
        return Submission(*tmp[0])
    except IndexError:
        return None

def get_submissions(user=None,reverse=True,all_subs=False):
    tmp = db_select(
        "dmob_submissions",
        where_condition="1 {0} {1}".format("AND deleted = 0" if not all_subs else "", "AND user = %s" if user is not None else ""),
        values=(user.id, ) if user is not None else (),
        extra="ORDER BY id {0}".format("DESC" if reverse else ""),
    )
    from models import Submission
    return [Submission(*x) for x in tmp]

def add_submission_case(testcase):
    db_insert("dmob_submission_cases", testcase.db_save())

def get_submission_cases(submission_id=None):
    tmp = db_select(
        "dmob_submission_cases",
        where_condition="submission_id = %s" if submission_id is not None else "",
        values=(submission_id,) if submission_id is not None else (),
    )
    from models import SubmissionTestCase
    return [SubmissionTestCase(*x) for x in tmp]

def add_judge(judge):
    global judge_list
    judge.id = db_insert("dmob_judges", judge.db_save())
    judge_list.append(judge)

def delete_judge(idx):
    global judge_list
    db_delete("dmob_judges", "id = %s", (judge_list[idx].id, ))
    del judge_list[idx]

async def load_user(bot, user_id):
    global users
    global discord_users_list
    try:
        return users[user_id]
    except KeyError:
        discord_users_list[user_id] = await bot.get_user_info(user_id)
        from models import Player
        users[user_id] = Player(user_id)
        return users[user_id]

async def load(bot):
    global loading    
    loading = True
    global problem_list
    global contest_list
    global discord_users_list
    global users
    global judgeserver
    global judge_list
    global judges
    global locks
    
    global db
    db = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWD, MYSQL_DATABASE)
    cursor = db.cursor()

    locks["problem"] = defaultdict(lambda: asyncio.Lock())
    locks["submissions"] = defaultdict(lambda: asyncio.Lock())
    locks["judge"] = defaultdict(lambda: asyncio.Lock())
    locks["user"] = defaultdict(lambda: asyncio.Lock())
    locks["contest"] = defaultdict(lambda: asyncio.Lock())
    locks["db"] = defaultdict(lambda: threading.RLock())
    
    from bridge import JudgeHandler, JudgeServer
    from models import Problem, Contest, Player, Judge
    
    judgeserver = JudgeServer(BRIDGED_IP_ADDRESS, JudgeHandler)
    threading.Thread(target=judgeserver.serve_forever).start()
    
    for x in db_select("dmob_problem"):
        problem_list[x[2]] = Problem(*x)

    for x in db_select("dmob_user"):
        discord_users_list[x[0]] = await bot.get_user_info(x[0])
        users[x[0]] = Player(*x)

    for x in db_select("dmob_contest"):
        cursor.execute("SELECT problem FROM dmob_contest_problem WHERE contest_id = %s", (x[0], ))
        contest_list[x[1]] = Contest(*x, [y[0] for y in cursor.fetchall()])

    for x in db_select("dmob_judges"):
        judge_list.append(Judge(*x))
    
    cursor.close()
    loading = False

async def save():
    global games
    global users
    global judgeserver
    global judges
    global locks
    
    for i, x in locks.items():
        if i != "db":
            for y in x.values():
                with await y:
                    pass
    
    for x in judges.values():
        x.terminate()
    judgeserver.stop()
    
    for x in games.values():
        await x.release_submissions()

    db_delete("dmob_user")
    for x in users.values():
        db_insert("dmob_user", x.db_save())
