import os
import threading
import time

from event_socket_server import get_preferred_engine
from .judgelist import JudgeList
from models import Judge

class JudgeServer(get_preferred_engine()):
    def __init__(self, *args, **kwargs):
        super(JudgeServer, self).__init__(*args, **kwargs)
        self.judges = JudgeList()
        self.judge_auth = []
        f = open("judges/auth", "r")
        for x in f.read().split('\n'):
            try:
                self.judge_auth.append(Judge(x.split(' ')[0], x.split(' ')[1]))
            except IndexError:
                pass
        f.close()
        self.ping_judge_thread = threading.Thread(target=self.ping_judge, args=())
        self.ping_judge_thread.daemon = True
        self.ping_judge_thread.start()

    def on_shutdown(self):
        super(JudgeServer, self).on_shutdown()

    def ping_judge(self):
        try:
            while True:
                for judge in self.judges:
                    judge.ping()
                time.sleep(10)
        except:
            raise
