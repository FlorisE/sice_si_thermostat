import threading
import time
import sys

class Sensor(object):
  def __init__(self, room):
    self.room = room

  def sense(self):
    return self.room.temperature


class Actuator(object):
  def __init__(self, room):
    self.room = room
    self.state = "OFF"

  def cool(self):
    self.room.temperature -= 0.1

  def heat(self):
    self.room.temperature += 0.1


class Thermostat(threading.Thread):
  def __init__(self, sensor, actuator, target, slack=0.5):
    super().__init__()
    self.sensor = sensor
    self.actuator = actuator
    self.target = target
    self.running = False
    self.slack = slack

  def run(self):
    self.running = True
    while self.running:
      if self.sensor.sense() > self.target + self.slack:
        self.actuator.state = "COOLING"
        while self.sensor.sense() > self.target and self.running:
          self.actuator.cool()
          time.sleep(0.5)
        self.actuator.state = "OFF"
      elif self.sensor.sense() < self.target - self.slack:
        self.actuator.state = "HEATING"
        while self.sensor.sense() < self.target and self.running:
          self.actuator.heat()
          time.sleep(0.5)
        self.actuator.state = "OFF"
      time.sleep(5)


class OutsideTemperature(threading.Thread):
  def __init__(self, room, temperature):
    super().__init__()
    self.room = room
    self.temperature = temperature
    self.running = False

  def run(self):
    self.running = True
    while self.running:
      temp_diff = self.temperature - self.room.temperature
      self.room.temperature += temp_diff / 50
      time.sleep(1)


class Room(object):
  def __init__(self, initial_temperature):
    self.temperature = initial_temperature


if __name__ == "__main__":
  room = Room(float(sys.argv[1]))
  sensor = Sensor(room)
  actuator = Actuator(room)
  thermostat = Thermostat(sensor, actuator, float(sys.argv[2]))
  temp_outside = OutsideTemperature(room, float(sys.argv[1]))
  thermostat.start()
  temp_outside.start()
  input()
  thermostat.running = False
  temp_outside.running = False
  thermostat.join()
  temp_outside.join()
