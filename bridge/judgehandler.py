from __future__ import division

import json
import time
from collections import deque

from event_socket_server import ZlibPacketHandler, ProxyProtocolMixin
from models import SubmissionTestCase, Submission, Judge

class JudgeHandler(ProxyProtocolMixin, ZlibPacketHandler):
    def __init__(self, server, socket):
        super(JudgeHandler, self).__init__(server, socket)
        self.handlers = {
            'grading-begin': self.on_grading_begin,
            'grading-end': self.on_grading_end,
            'compile-error': self.on_compile_error,
            'compile-message': self.on_compile_message,
            'batch-begin': self.on_batch_begin,
            'batch-end': self.on_batch_end,
            'test-case-status': self.on_test_case,
            'internal-error': self.on_internal_error,
            'submission-terminated': self.on_submission_terminated,
            'submission-acknowledged': self.on_submission_acknowledged,
            'ping-response': self.on_ping_response,
            'supported-problems': self.on_supported_problems,
            'handshake': self.on_handshake,
        }
        self._to_kill = True
        self._working = False
        self._no_response_job = None
        self._problems = []
        self.executors = []
        self.problems = {}
        self.latency = None
        self.time_delta = None
        self.load = 1e100
        self.name = None
        self.batch_id = None
        self.in_batch = False
        self._ping_average = deque(maxlen=6)  # 1 minute average, just like load
        self._time_delta = deque(maxlen=6)

        self.server.schedule(15, self._kill_if_no_auth)

        self.cases = []

    def _kill_if_no_auth(self):
        if self._to_kill:
            self.close()

    def on_close(self):
        self._to_kill = False
        if self._no_response_job:
            self.server.unschedule(self._no_response_job)
        self.server.judges.remove(self)

    def _authenticate(self, id, key):
        return Judge(id, key) in self.server.judge_auth

    def _format_send(self, data):
        return super(JudgeHandler, self)._format_send(json.dumps(data, separators=(',', ':')))

    def on_handshake(self, packet):
        if 'id' not in packet or 'key' not in packet:
            self.close()
            return
        if not self._authenticate(packet['id'], packet['key']):
            print(packet['id'] + " failed authentication")
            self.close()
            return

        self._to_kill = False
        self._problems = packet['problems']
        self.problems = dict(self._problems)
        self.executors = packet['executors']
        self.name = packet['id']
        self.send({'name': 'handshake-success'})
        self.server.judges.register(self)

    def can_judge(self, problem, executor):
        return problem in self.problems and executor in self.executors

    @property
    def working(self):
        return bool(self._working)

    def submit(self, id, problem, time, memory, language, source):
        self._working = id
        self._no_response_job = self.server.schedule(20, self._kill_if_no_response)
        self.send({
            'name': 'submission-request',
            'submission-id': id,
            'problem-id': problem,
            'language': language,
            'source': source,
            'time-limit': time,
            'memory-limit': memory,
            'short-circuit': True,
            'pretests-only': False,
        })

    def _kill_if_no_response(self):
        self.close()

    def malformed_packet(self, exception):
        super(JudgeHandler, self).malformed_packet(exception)

    def on_submission_processing(self, packet):
        pass

    def on_submission_wrong_acknowledge(self, packet, expected, got):
        pass

    def on_submission_acknowledged(self, packet):
        if not packet.get('submission-id', None) == self._working:
            self.on_submission_wrong_acknowledge(packet, self._working, packet.get('submission-id', None))
            self.close()
        if self._no_response_job:
            self.server.unschedule(self._no_response_job)
            self._no_response_job = None
        self.on_submission_processing(packet)

    def abort(self):
        self.send({'name': 'terminate-submission'})

    def get_current_submission(self):
        return self._working or None

    def ping(self):
        self.send({'name': 'ping', 'when': time.time()})

    def packet(self, data):
        try:
            try:
                data = json.loads(data)
                if 'name' not in data:
                    raise ValueError
            except ValueError:
                self.on_malformed(data)
            else:
                handler = self.handlers.get(data['name'], self.on_malformed)
                handler(data)
        except:
            self._packet_exception()

    def _packet_exception(self):
        pass

    def _submission_is_batch(self, id):
        pass

    def on_supported_problems(self, packet):
        self._problems = packet['problems']
        self.problems = dict(self._problems)
        if not self.working:
            self.server.judges.update_problems(self)

    def on_grading_begin(self, packet):
        self.cases = []
        self.batch_id = None
    
    def set_submission(self, id, points, total, time, memory, status_code):
        user = self.server.judges.submission_info[id][0]
        problem = self.server.judges.submission_info[id][1]
        self.server.judges.finished_submissions[id] = Submission(id, points, total, time, memory, status_code, user, problem)

    def on_grading_end(self, packet):
        time = 0
        memory = 0
        points = 0.0
        total = 0
        status = 0
        status_codes = ['SC', 'AC', 'WA', 'MLE', 'TLE', 'IR', 'RTE', 'OLE']
        batches = {}  # batch number: (points, total)

        for case in self.cases:
            time += case.time
            if not case.batch:
                points += case.points
                total += case.total
            else:
                if case.batch in batches:
                    batches[case.batch][0] = min(batches[case.batch][0], case.points)
                    batches[case.batch][1] = max(batches[case.batch][1], case.total)
                else:
                    batches[case.batch] = [case.points, case.total]
            memory = max(memory, case.memory)
            i = status_codes.index(case.status)
            if i > status:
                status = i
        for i in batches:
            points += batches[i][0]
            total += batches[i][1]
        points = round(points, 1)
        total = round(total, 1)
        self.set_submission(packet['submission-id'], points, total, time, memory, status_codes[status])
        self._free_self(packet)
        self.batch_id = None

    def on_compile_error(self, packet):
        self.set_submission(packet['submission-id'], 0.0, 0.0, 0, 0, 'CE')
        self._free_self(packet)

    def on_compile_message(self, packet):
        pass
    def on_internal_error(self, packet):
        self.set_submission(packet['submission-id'], 0.0, 0.0, 0, 0, 'IE')
        self._free_self(packet)

    def on_submission_terminated(self, packet):
        self._free_self(packet)

    def on_batch_begin(self, packet):
        self.in_batch = True
        if self.batch_id is None:
            self.batch_id = 0
            self._submission_is_batch(packet['submission-id'])
        self.batch_id += 1

    def on_batch_end(self, packet):
        self.in_batch = False

    def on_test_case(self, packet, max_feedback=100):
        id = packet['submission-id']
        test_case = SubmissionTestCase(submission_id=id, case=packet['position'])
        status = packet['status']
        if status & 4:
            test_case.status = 'TLE'
        elif status & 8:
            test_case.status = 'MLE'
        elif status & 64:
            test_case.status = 'OLE'
        elif status & 2:
            test_case.status = 'RTE'
        elif status & 16:
            test_case.status = 'IR'
        elif status & 1:
            test_case.status = 'WA'
        elif status & 32:
            test_case.status = 'SC'
        else:
            test_case.status = 'AC'
        test_case.time = packet['time']
        test_case.memory = packet['memory']
        test_case.points = packet['points']
        test_case.total = packet['total-points']
        test_case.batch = self.batch_id if self.in_batch else None
        test_case.feedback = (packet.get('feedback', None) or '')[:max_feedback]
        test_case.output = packet['output']
        self.cases.append(test_case)
    
    def on_malformed(self, packet):
        pass
    def on_ping_response(self, packet):
        end = time.time()
        self._ping_average.append(end - packet['when'])
        self._time_delta.append((end + packet['when']) / 2 - packet['time'])
        self.latency = sum(self._ping_average) / len(self._ping_average)
        self.time_delta = sum(self._time_delta) / len(self._time_delta)
        self.load = packet['load']

    def _free_self(self, packet):
        self._working = False
        self.server.judges.on_judge_free(self, packet['submission-id'])
