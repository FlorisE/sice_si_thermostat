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

  @property
  def state(self):
    return self._state

  @state.setter
  def state(self, new_state):
    print(f"Test Case {self.name} transitioning from {self.state} to {new_state}")
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

    use_timer = self.max_duration != 0

    if use_timer:
      current_time = time.time()
    
    self.state = "Evaluating invariants, preempts and postconditions"
    while self.running:
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
      time.sleep(SLEEP_TIME)

  def finish(self, success, message=None):
    self.result = TestCaseResult(success, message)
    self.state = "Finished"
    self.running = False

def print_status(test_case):
  if test_case.result is None:
    print(f"Test Case {test_case.name} Running")
    return

  status = "SUCCESS" if test_case.result.success else "FAILED"
  if test_case.result.message:
    print(f"Test Case {test_case.name} {status} {test_case.result.message}")
  else:
    print(f"Test Case {test_case.name} {status}")


class TestRunner(threading.Thread):
  def __init__(self, test_cases, finalizer=None):
    super().__init__()
    self.test_cases = test_cases
    self.finalizer = finalizer
    self.running = False

  def run(self):
    self.running = True

    for test_case in self.test_cases:
      test_case.start()
  
    report_time = time.time() + 10
  
    while self.running:
      for test_case in self.test_cases:
        test_case.join(0.05)
      if time.time() > report_time:
        for test_case in self.test_cases:
          print_status(test_case)
        report_time = time.time() + 10
      if all([test_case.state == "Finished" for test_case in self.test_cases]):
        self.running = False
        if self.finalizer:
          self.finalizer()
  
      time.sleep(SLEEP_TIME)
  
    for test_case in self.test_cases:
      print_status(test_case)
