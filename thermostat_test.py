from thermostat import Room, Sensor, Actuator, Thermostat, OutsideTemperature
from test_framework import TestCase, TestRunner
import threading
import time

outside_temperature = 20.
target_temperature = 22.

room = Room(outside_temperature)
sensor = Sensor(room)
actuator = Actuator(room)
thermostat = Thermostat(sensor, actuator, target_temperature)
outside_temperature_mod = OutsideTemperature(room, outside_temperature)

tc0 = TestCase(name="Heat if current temperature is below target",
         preconditions=[
           lambda: actuator.state == "OFF",
           lambda: room.temperature < thermostat.target - thermostat.slack
         ],
         invariants=[
           lambda: actuator.state == "HEATING"
         ],
         invariants_at_least_once=True,
         postconditions=[
           lambda: actuator.state == "OFF",
           lambda: room.temperature >= thermostat.target - thermostat.slack,
           lambda: room.temperature <= thermostat.target + thermostat.slack
         ])

tc1 = TestCase(name="Cool if current temperature is above target",
         preconditions=[
           lambda: actuator.state == "OFF",
           lambda: room.temperature > thermostat.target + thermostat.slack
         ],
         invariants=[
           lambda: actuator.state == "COOLING"
         ],
         invariants_at_least_once=True,
         postconditions=[
           lambda: actuator.state == "OFF",
           lambda: room.temperature >= thermostat.target - thermostat.slack,
           lambda: room.temperature <= thermostat.target + thermostat.slack
         ])

tc2 = TestCase(name="Do nothing if current temperature is on target",
         preconditions=[
           lambda: actuator.state == "OFF",
           lambda: room.temperature >= thermostat.target - thermostat.slack,
           lambda: room.temperature <= thermostat.target + thermostat.slack
         ],
         invariants=[
           lambda: actuator.state == "OFF"
         ],
         preempts=[
           lambda: room.temperature <= thermostat.target - thermostat.slack or room.temperature >= thermostat.target + thermostat.slack
	 ],
         postconditions=[
           lambda: actuator.state == "OFF"
         ])


class DataPrinter(threading.Thread):
  def __init__(self, room, thermostat, actuator):
    super().__init__()
    self.room = room
    self.thermostat = thermostat
    self.actuator = actuator
    self.running = False

  def run(self):
    self.running = True
    while self.running:
      print(f"Room temperature: {self.room.temperature} Thermostat target: {self.thermostat.target} Thermostat slack: {self.thermostat.slack} Actuator state: {self.actuator.state}")
      time.sleep(0.5)


class ChangeConditions(threading.Thread):
  def __init__(self, outside_temperature):
    super().__init__()
    self.outside_temperature = outside_temperature

  def run(self):
    start_time = time.time()
    while True:
      if time.time() > start_time + 60:
        self.outside_temperature.temperature = 24
        break

def cleanup(dp):
  dp.running = False
  dp.join()

dp = DataPrinter(room, thermostat, actuator)
dp.start()
tr = TestRunner([tc0, tc1, tc2], lambda: cleanup(dp))
tr.start()
thermostat.start()
outside_temperature_mod.start()
cc = ChangeConditions(outside_temperature_mod)
cc.start()
input()
