import threading
import time

SLEEP_TIME = 0.1


class TestCaseResult(object):
  def __init__(self, success, message=None):
    self.success = success
    self.message = message


class TestCase(threading.Thread):
  def __init__(self, name, preconditions, invariants, postconditions, invariants_at_least_once=False, max_duration=0, preempts=[]):
    super().__init__()
    self.name = name
    self.preconditions = preconditions
    self.invariants = invariants
    self.postconditions = postconditions
    self.preempts = preempts
    self.max_duration = max_duration
    self._state = "Initialized"
    self.result = None
    self.invariants_at_least_once = invariants_at_least_once
    self.running = False

  @property
  def state(self):
    return self._state

  @state.setter
  def state(self, new_state):
    print(f"{self.name:<60} {self.state:<50} {new_state:<50}")
    self._state = new_state

  def evaluate_preconditions(self):
    precondition_results = [precondition() for precondition in self.preconditions]
    return all(precondition_results)

  def evaluate_invariants(self):
    invariant_results = [invariant() for invariant in self.invariants]
    return all(invariant_results)

  def evaluate_preempts(self):
    preempts = [preempt() for preempt in self.preempts]
    return all(preempts)

  def evaluate_postconditions(self):
    postcondition_results = [postcondition() for postcondition in self.postconditions]
    return all(postcondition_results)

  def run(self):
    self.state = "Running"
    self.running = True

    self.state = "Evaluating preconditions"
    while self.running and not self.evaluate_preconditions():
      time.sleep(SLEEP_TIME)

    if self.running:
      use_timer = self.max_duration != 0

      if use_timer:
        current_time = time.time()
      
      self.state = "Evaluating invariants, preempts and postconditions"

    while self.running:
      time.sleep(SLEEP_TIME)
      if use_timer:
        time_condition = time.time() < current_time + self.max_duration 
      preempts = self.evaluate_preempts()
      invariants = self.evaluate_invariants()
      post_conditions = self.evaluate_postconditions()
      if self.invariants_at_least_once and not invariants:
        continue
      if preempts:
        self.finish(True)
        break
      if post_conditions:
        self.finish(True)
        break
      if use_timer and not time_condition:
        self.finish(False, "Time out")
        break
      if not invariants:
        self.finish(False, "Invariants")
        break

  def finish(self, success, message=None):
    self.result = TestCaseResult(success, message)
    self.state = "Finished"
    self.running = False

def print_status(test_case):
  if test_case.result is None:
    print(f"{test_case.name:<60} No result")
    return

  status = "SUCCESS" if test_case.result.success else "FAILED"
  if test_case.result.message:
    print(f"{test_case.name:<60} {status:<50} {test_case.result.message}")
  else:
    print(f"{test_case.name:<60} {status}")


class TestRunner(threading.Thread):
  def __init__(self, test_cases, finalizer=None):
    super().__init__()
    self.test_cases = test_cases
    self.finalizer = finalizer
    self.running = False

  def run(self):
    self.running = True

    print("{0:<60} {1:<50} {2:<50}".format("TEST CASE", "FROM", "TO"))
    for test_case in self.test_cases:
      test_case.start()
  
    while self.running:
      if all([test_case.state == "Finished" for test_case in self.test_cases]):
        self.running = False
        if self.finalizer:
          self.finalizer()
      time.sleep(SLEEP_TIME)
  
    print()
    print("{0:<60} {1:<50} {2}".format("TEST CASE", "STATUS", "MESSAGE"))
    for test_case in self.test_cases:
      if test_case.running:
          test_case.finish(False, "Terminated")
      test_case.join()
      print_status(test_case)
