import sys
from PySide2 import QtCore, QtWidgets, QtGui

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.room_temp_label = QtWidgets.QLabel("Room Temperature")
        self.room_temp = QtWidgets.QLabel("0")
        self.outside_temp_label = QtWidgets.QLabel("Outside Temperature")
        self.outside_temp = QtWidgets.QLabel("0")
        self.actuator_status_label = QtWidgets.QLabel("Actuator Status")
        self.actuator_status = QtWidgets.QLabel("none")
        self.thermostat_slack_label = QtWidgets.QLabel("Thermostat Slack")
        self.thermostat_slack = QtWidgets.QLabel("0")
        self.thermostat_target_label = QtWidgets.QLabel("Thermostat Target")
        self.thermostat_target = QtWidgets.QLabel("0")
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.room_temp_label, 0, 0)
        self.layout.addWidget(self.room_temp, 1, 0)
        self.layout.addWidget(self.outside_temp_label, 0, 1)
        self.layout.addWidget(self.outside_temp, 1, 1)
        self.layout.addWidget(self.actuator_status_label, 0, 2)
        self.layout.addWidget(self.actuator_status, 1, 2)
        self.layout.addWidget(self.thermostat_slack_label, 0, 3)
        self.layout.addWidget(self.thermostat_slack, 1, 3)
        self.layout.addWidget(self.thermostat_target_label, 0, 4)
        self.layout.addWidget(self.thermostat_target, 1, 4)
        self.setLayout(self.layout)

    def updateRoomTemperature(self, room_temperature):
        self.room_temp.setText(str(room_temperature))

    def updateOutsideTemperature(self, outside_temperature):
        self.outside_temp.setText(str(outside_temperature))

    def updateActuatorStatus(self, actuator_status):
        self.actuator_status.setText(actuator_status)

    def updateThermostatSlack(self, slack):
        self.thermostat_slack.setText(str(slack))

    def updateThermostatTarget(self, target):
        self.thermostat_target.setText(str(target))

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(1000, 100)
    widget.show()

    sys.exit(app.exec_())
