import asyncio
import pymysql
import threading
from collections import defaultdict
from util import *
from settings import *


problem_list = {}
discord_users_list = {}
discord_channels_list = {}
users = {}
games = {}
locks = {}
judgeserver = None
judges = {}
loading = False
db = None


def sql_format(arr):
    return ", ".join(["%s"]*len(arr))


def parse_args(*args):
    return tuple(x for x in args if x is not None)


def db_insert(table, values):
    global db
    with locks["db"]["read"] and locks["db"]["write"]:
        cursor = db.cursor()
        cursor.execute("""\
            INSERT INTO {0} VALUES ({1})
        """.format(table, sql_format(values)), values)
        cursor.close()
        db.commit()
        values = cursor.lastrowid
        del cursor
        return values


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
        values = cursor.fetchall()
        cursor.close()
        del cursor
        return values


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


def db_update(table, id, field="deleted", value="1"):
    global db
    with locks["db"]["read"] and locks["db"]["write"]:
        cursor = db.cursor()
        cursor.execute("""\
            UPDATE {0}
            SET {1} = %s
            WHERE id = %s
        """.format(table, field), (value, id)
        )
        cursor.close()
        db.commit()


def add_contest(contest):
    id = db_insert("dmob_contest", contest.db_save())
    for x, y in enumerate(contest._problems, 1):
        db_insert("dmob_contest_problem", (None, id, x, y))


def get_contests(deleted_contests=False, name=None, id=None):
    tmp = db_select(
        "dmob_contest",
        where_condition="1 {0} {1} {2}".format(
            "AND deleted = 0" if not deleted_contests else "",
            "AND name = %s" if name is not None else "",
            "AND id = %s" if id is not None else "",
        ),
        values=parse_args(name, id),
        extra="ORDER BY id DESC",
    )
    from models import Contest
    contests = []
    for x in tmp:
        problems = db_select(
            "dmob_contest_problem",
            where_condition="contest_id = %s",
            values=(x[0],),
        )
        contests.append(Contest(*x[0:2], [y[3] for y in problems], *x[2:]))
    return contests


def delete_contest(contest):
    db_update("dmob_contest", contest.id)


def create_game(game):
    return db_insert("dmob_game", game.db_save())


def update_game_state(game):
    db_update("dmob_game", game.id, "state", game.contest_state)


def get_game(channel_id, bot=None):
    tmp = db_select(
        "dmob_game",
        where_condition="id = (SELECT MAX(id) from dmob_game WHERE channel = %s)",
        values=(channel_id,),
    )
    import DMOBGame
    return None if len(tmp) == 0 else DMOBGame(bot, *tmp[0])


def add_problem(problem):
    global problem_list
    problem.id = db_insert("dmob_problem", problem.db_save())
    problem_list[problem.code] = problem
    return problem.id


def change_problem(problem, field, new_value):
    global problem_list
    db_update("dmob_problem", problem.id, field, new_value)
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
        UPDATE dmob_submission
        SET points=%s, total=%s, time=%s, memory=%s, result=%s
        WHERE id = %s
    """, (sub.points, sub.total, sub.time, sub.memory, sub.result, sub.submission_id))
    cursor.close()
    db.commit()


def create_submission(sub):
    return db_insert("dmob_submission", sub.db_save())


def delete_submission(sub):
    db_update("dmob_submission", sub.submission_id)


def get_submissions(user=None, reverse=True, deleted_subs=False, contest_subs=False, id=None):
    global db
    cursor = db.cursor()
    cursor.execute("""\
        SELECT sub.*
        FROM dmob_submission sub
            LEFT JOIN dmob_game game
        ON game.id = sub.contest
        WHERE 1 {0} {1} {2} {3}
        ORDER BY sub.id {4}
    """.format(
            "AND (game.state = 3 OR sub.contest IS NULL)" if not contest_subs else "",
            "AND sub.deleted = 0" if not deleted_subs else "",
            "AND sub.user = %s" if user is not None else "",
            "AND sub.id = %s" if id is not None else "",
            "DESC" if reverse else "",
        ),
        parse_args(user, id),
    )
    cursor.close()
    tmp = cursor.fetchall()
    from models import Submission
    return [Submission(*x) for x in tmp]


def get_best_submissions(user):
    global db
    cursor = db.cursor()
    cursor.execute("""\
        SELECT sub.problem, MAX(sub.points/sub.total*problem.point_value) AS best, MIN(sub.submission_time) AS first
        FROM dmob_submission sub
            LEFT JOIN dmob_problem problem ON problem.code = sub.problem
            LEFT JOIN dmob_game game ON game.id = sub.contest
        WHERE (game.state = 3 OR sub.contest IS NULL) AND sub.user = %s
                AND sub.deleted = 0 AND sub.result NOT IN ("QU", "IE", "CE")
        GROUP BY sub.problem
        ORDER BY best, first
    """, (user.id,))
    cursor.close()
    return cursor.fetchall()


def get_best_contest_submissions(user, game):
    global db
    cursor = db.cursor()
    cursor.execute("""\
        SELECT cp.problem_position, MAX(sub.points/sub.total) AS best, MIN(sub.submission_time) AS first
        FROM dmob_submission sub
            LEFT JOIN dmob_game game ON game.id = sub.contest
            LEFT JOIN dmob_contest_problem cp ON cp.problem = sub.problem AND cp.contest_id = game.contest
        WHERE sub.deleted = 0 AND sub.user = %s AND sub.result NOT IN ("QU", "IE", "CE") AND sub.contest = %s
                AND (sub.points/sub.total) = (
                    SELECT MAX(points/total)
                    FROM dmob_submission
                    WHERE contest = %s AND user = %s AND sub.problem = problem
                )
        GROUP BY sub.problem
        ORDER BY cp.problem_position
    """, (user.id, game.id, game.id, user.id))
    cursor.close()
    tmp = cursor.fetchall()
    best_subs = [[0, 0]]*len(game.contest.problems)
    for x in tmp:
        best_subs[x[0]-1] = [x[1]*100, (x[2]-game.start_time).total_seconds()]
    return best_subs


def add_submission_case(testcase):
    db_insert("dmob_submission_case", testcase.db_save())


def get_submission_cases(submission_id=None):
    tmp = db_select(
        "dmob_submission_case",
        where_condition="submission_id = %s" if submission_id is not None else "",
        values=(submission_id,) if submission_id is not None else (),
    )
    from models import SubmissionTestCase
    return [SubmissionTestCase(*x) for x in tmp]


def add_judge(judge):
    db_insert("dmob_judge", judge.db_save())


def get_judges(deleted_judges=False, name=None, id=None):
    tmp = db_select(
        "dmob_judge",
        where_condition="1 {0} {1} {2}".format(
                "AND deleted = 0" if not deleted_judges else "",
                "AND name = %s" if name is not None else "",
                "AND id = %s" if id is not None else "",
            ),
        values=parse_args(name, id),
    )
    from models import Judge
    return [Judge(*x) for x in tmp]


def authenticate_judge(id, key):
    tmp = db_select(
        "dmob_judge",
        where_condition="deleted = 0 AND name = %s AND `key` = %s",
        values=(id, key),
    )
    return len(tmp) > 0


def delete_judge(judge):
    db_update("dmob_judge", judge.id)


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
    global discord_users_list
    global users
    global judgeserver
    global judges
    global locks

    global db
    db = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWD, MYSQL_DATABASE)

    locks["problem"] = defaultdict(lambda: asyncio.Lock())
    locks["submissions"] = defaultdict(lambda: asyncio.Lock())
    locks["judge"] = defaultdict(lambda: asyncio.Lock())
    locks["user"] = defaultdict(lambda: asyncio.Lock())
    locks["contest"] = defaultdict(lambda: asyncio.Lock())
    locks["db"] = defaultdict(lambda: threading.RLock())

    from bridge import JudgeHandler, JudgeServer
    from models import Problem, Player

    judgeserver = JudgeServer(BRIDGED_IP_ADDRESS, JudgeHandler)
    threading.Thread(target=judgeserver.serve_forever).start()

    for x in db_select("dmob_problem"):
        problem_list[x[2]] = Problem(*x)

    for x in db_select("dmob_user"):
        discord_users_list[x[0]] = await bot.get_user_info(x[0])
        users[x[0]] = Player(*x)

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

    db_delete("dmob_user")
    for x in users.values():
        db_insert("dmob_user", x.db_save())
    db.close()
