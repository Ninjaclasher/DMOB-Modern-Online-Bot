from collections import namedtuple
from operator import attrgetter
from threading import RLock

try:
    from llist import dllist
except ImportError:
    from pyllist import dllist

PriorityMarker = namedtuple('PriorityMarker', 'priority')

class JudgeList(object):
    priorities = 2

    def __init__(self):
        self.queue = dllist()
        self.priority = [self.queue.append(PriorityMarker(i)) for i in range(self.priorities)]
        self.judges = set()
        self.submission_map = {}
        self.finished_submissions = {}
        self.lock = RLock()

    def _handle_free_judge(self, judge):
        with self.lock:
            node = self.queue.first
            while node:
                if not isinstance(node.value, PriorityMarker):
                    id, problem, time, memory, language, source = node.value
                    if judge.can_judge(problem, language):
                        self.submission_map[id] = judge
                        try:
                            judge.submit(id, problem, time, memory, language, source)
                        except Exception:
                            self.judges.remove(judge)
                            return
                        self.queue.remove(node)
                        break
                node = node.next

    def register(self, judge):
        print(judge.name + " connected")
        with self.lock:
            self.judges.add(judge)
            self._handle_free_judge(judge)

    def update_problems(self, judge):
        with self.lock:
            self._handle_free_judge(judge)

    def remove(self, judge):
        print(judge.name + " disconnected")
        with self.lock:
            sub = judge.get_current_submission()
            if sub is not None:
                try:
                    del self.submission_map[sub]
                except KeyError:
                    pass
            self.judges.discard(judge)

    def __iter__(self):
        return iter(self.judges)

    def on_judge_free(self, judge, submission):
        with self.lock:
            del self.submission_map[submission]
            self._handle_free_judge(judge)

    def abort(self, submission):
        with self.lock:
            self.submission_map[submission].abort()

    def check_priority(self, priority):
        return 0 <= priority < self.priorities

    def judge(self, id, problem, time, memory, language, source, priority=1):
        with self.lock:
            if id in self.submission_map:
                return

            candidates = [judge for judge in self.judges if not judge.working and judge.can_judge(problem, language)]
            if candidates: 
                judge = min(candidates, key=attrgetter('load'))
                self.submission_map[id] = judge
                try:
                    judge.submit(id, problem, time, memory, language, source)
                except Exception:
                    self.judges.discard(judge)
                    return self.judge(id, problem, time, memory, language, source, priority)
            else:
                self.queue.insert((id, problem, time, memory, language, source), self.priority[priority])
