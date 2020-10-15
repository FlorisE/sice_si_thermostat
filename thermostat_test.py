from PySide2 import QtWidgets
from thermostat import Room, Sensor, Actuator, Thermostat, OutsideTemperature
from thermostat_gui import MyWidget
from test_framework import TestCase, TestRunner
import threading
import time
import sys

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
  def __init__(self, room, thermostat, actuator, outside_temperature, widget):
    super().__init__()
    self.room = room
    self.thermostat = thermostat
    self.actuator = actuator
    self.outside_temperature = outside_temperature
    self.running = False
    self.widget = widget

  def run(self):
    self.running = True
    while self.running:
      self.widget.updateRoomTemperature(self.room.temperature)
      self.widget.updateOutsideTemperature(self.outside_temperature.temperature)
      self.widget.updateActuatorStatus(self.actuator.state)
      self.widget.updateThermostatSlack(self.thermostat.slack)
      self.widget.updateThermostatTarget(self.thermostat.target)
      time.sleep(0.1)


class ChangeConditions(threading.Thread):
  def __init__(self, outside_temperature):
    super().__init__()
    self.outside_temperature = outside_temperature
    self.running = False

  def run(self):
    self.running = True
    start_time = time.time()
    while self.running:
      if time.time() > start_time + 60:
        self.outside_temperature.temperature = 24
        break
      time.sleep(0.01)

app = QtWidgets.QApplication([])
widget = MyWidget()
widget.resize(1000, 100)
widget.show()

dp = DataPrinter(room, thermostat, actuator, outside_temperature_mod, widget)
dp.start()
tr = TestRunner([tc0, tc1, tc2])
tr.start()
thermostat.start()
outside_temperature_mod.start()
cc = ChangeConditions(outside_temperature_mod)
cc.start()
app.exec_()
outside_temperature_mod.running = False
thermostat.running = False
tr.running = False
cc.running = False
dp.running = False
dp.join()
cc.join()
tr.join()
thermostat.join()
outside_temperature_mod.join()
