#
#   Copyright (C) 2008-2015 by Nicolas Piganeau
#   npi@m4x.org
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the
#   Free Software Foundation, Inc.,
#   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
from math import sqrt

from Qt import QtCore, QtGui, QtWidgets, Qt
from ts2 import utils
from ts2.routing import position
from ts2.scenery import lineitem, enditem
from ts2.scenery.signals import signalaspect, signalitem

translate = QtWidgets.qApp.translate


class TrainStatus(QtCore.QObject):
    """Holds the enum describing the status of a
    :class:`~ts2.trains.train.Train`"""

    INACTIVE = 0
    """Not yet entered on the scene"""

    RUNNING = 10
    """Running with a positive speed"""

    STOPPED = 20
    """Scheduled stop, e.g. at a station"""

    WAITING = 30
    """Unscheduled stop, e.g. at a red signal"""

    OUT = 40
    """Exited the area"""

    END_OF_SERVICE = 50
    """Ended its service and no new service assigned"""

    @classmethod
    def text(cls, status):
        """
        :return: Text corresponding to each status to display in the application
        :rtype: str
        """
        if status == cls.INACTIVE:
            return translate("TrainStatus", "Inactive")

        elif status == cls.RUNNING:
            return translate("TrainStatus", "Running")

        elif status == cls.STOPPED:
            return translate("TrainStatus", "Stopped at station")

        elif status == cls.WAITING:
            return translate("TrainStatus", "Waiting at red signal")

        elif status == cls.OUT:
            return translate("TrainStatus", "Exited the area")

        elif status == cls.END_OF_SERVICE:
            return translate("TrainStatus", "End of service")

        else:
            return ""


class TrainListModel(QtCore.QAbstractTableModel):
    """Model for displaying trains as a list during the game.
    """
    def __init__(self, simulation):
        """Constructor for the TrainListModel class"""
        super().__init__()
        self.simulation = simulation

    def rowCount(self, parent=QtCore.QModelIndex(), *args):
        """Returns the number of rows of the model, corresponding to the
        number of trains of the simulation"""
        return len(self.simulation.trains)

    def columnCount(self, parent=QtCore.QModelIndex(), *args):
        """Returns the number of columns of the model
        @TODO ?? wtf
        """

        return 8

    def data(self, index, role=Qt.DisplayRole):
        """Returns the data at the given index"""
        train = self.simulation.trains[index.row()]
        if train.nextPlaceIndex is not None:
            line = train.currentService.lines[train.nextPlaceIndex]
        else:
            line = None
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return train.serviceCode
            elif index.column() == 1:
                return TrainStatus.text(train.status)
            elif index.column() == 2 and train.currentService:
                return train.currentService.entryPlaceName
            elif index.column() == 3 and train.currentService:
                return train.currentService.exitPlaceName
            elif index.column() == 4 and line is not None:
                return line.place.placeName
            elif index.column() == 5 and line is not None:
                return line.trackCode
            elif index.column() == 6 and line is not None:
                if line.mustStop:
                    return line.scheduledArrivalTime.toString("hh:mm:ss")
                else:
                    return self.tr("Non-stop")
            elif index.column() == 7 and line is not None:
                return line.scheduledDepartureTime.toString("hh:mm:ss")
            else:
                return ""
        elif role == Qt.ForegroundRole:
            if train.status == TrainStatus.RUNNING:
                return QtGui.QBrush(Qt.darkGreen)
            elif train.status == TrainStatus.STOPPED:
                return QtGui.QBrush(Qt.darkBlue)
            elif train.status == TrainStatus.WAITING:
                return QtGui.QBrush(Qt.red)
            else:
                return QtGui.QBrush(Qt.darkGray)
        return None

    def headerData(self, column, orientation, role=Qt.DisplayRole):
        """Returns the column headers to display"""
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if column == 0:
                return self.tr("Code")
            elif column == 1:
                return self.tr("Status")
            elif column == 2:
                return self.tr("Entry Point")
            elif column == 3:
                return self.tr("Exit Point")
            elif column == 4:
                return self.tr("Next place")
            elif column == 5:
                return self.tr("Track")
            elif column == 6:
                return self.tr("Arrival time")
            elif column == 7:
                return self.tr("Departure time")
            else:
                return ""
        return None

    def flags(self, index):
        """Returns the flags of the model"""
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    @QtCore.pyqtSlot(int)
    def update(self, trainId):
        """Emits the dataChanged signal for the train defined by trainId."""
        row = trainId
        self.dataChanged.emit(self.index(row, 0), self.index(row, 7))


class TrainsModel(QtCore.QAbstractTableModel):
    """Model for displaying trains as a list in the editor
    """
    def __init__(self, editor):
        """Constructor for the TrainsModel class"""
        super().__init__()
        self._editor = editor

    def rowCount(self, parent=None, *args):
        """Returns the number of rows of the model, corresponding to the
        number of trains of the editor"""
        return len(self._editor.trains)

    def columnCount(self, parent=None, *args):
        """Returns the number of columns of the model"""
        return 7

    def data(self, index, role=Qt.DisplayRole):
        """Returns the data at the given index"""
        if role == Qt.DisplayRole or role == Qt.EditRole:
            train = self._editor.trains[index.row()]
            if index.column() == 0:
                return index.row()
            elif index.column() == 1:
                return train.serviceCode
            elif index.column() == 2:
                return train.trainTypeCode
            elif index.column() == 3:
                return train.appearTimeStr
            elif index.column() == 4:
                return train.trainHeadStr
            elif index.column() == 5:
                return train.initialSpeed
            elif index.column() == 6:
                return train.initialDelayStr
            else:
                return ""
        return None

    def headerData(self, column, orientation, role=Qt.DisplayRole):
        """Returns the column headers to display"""
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if column == 0:
                return self.tr("id")
            elif column == 1:
                return self.tr("Service code")
            elif column == 2:
                return self.tr("Train type")
            elif column == 3:
                return self.tr("Entry time")
            elif column == 4:
                return self.tr("Entry position")
            elif column == 5:
                return self.tr("Entry speed")
            elif column == 6:
                return self.tr("Initial Delay")
            else:
                return ""
        return None

    def setData(self, index, value, role=None):
        """Updates data when modified in the view"""
        if role == Qt.EditRole:
            if index.column() == 1:
                self._editor.trains[index.row()].serviceCode = value
            elif index.column() == 2:
                self._editor.trains[index.row()].trainTypeCode = value
            elif index.column() == 3:
                self._editor.trains[index.row()].appearTimeStr = value
            elif index.column() == 4:
                self._editor.trains[index.row()].trainHeadStr = value
            elif index.column() == 5:
                self._editor.trains[index.row()].initialSpeed = value
            elif index.column() == 6:
                self._editor.trains[index.row()].initialDelayStr = value
            else:
                return False
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        """Returns the flags of the model"""
        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if index.column() != 0:
            flags |= Qt.ItemIsEditable
        return flags

    @property
    def simulation(self):
        """Returns the simulation this model is attached to."""
        return self._editor


class TrainInfoModel(QtCore.QAbstractTableModel):
    """Model for displaying a single service information in a view
    """
    def __init__(self, simulation):
        """Constructor for the TrainInfoModel class"""
        super().__init__()
        self.simulation = simulation
        self._train = None

    def rowCount(self, parent=None, *args, **kwargs):
        """Returns the number of rows in the model"""
        if self._train is not None:
            return 12
        else:
            return 0

    def columnCount(self, parent=None, *args, **kwargs):
        """Returns the number of columns of the model"""
        if self._train is not None:
            return 2
        else:
            return 0

    def data(self, index, role=Qt.DisplayRole):
        """Returns the data at the given index"""
        if self._train is not None:
            nextPlaceIndex = self._train.nextPlaceIndex
            if nextPlaceIndex is not None:
                line = self._train.currentService.lines[nextPlaceIndex]
            else:
                line = None
            if role == Qt.DisplayRole:
                if index.column() == 0:
                    if index.row() == 0:
                        return self.tr("Service Code:")
                    elif index.row() == 1:
                        return self.tr("Status")
                    elif index.row() == 2:
                        return self.tr("Speed:")
                    elif index.row() == 3:
                        return self.tr("Train Type:")
                    elif index.row() == 4:
                        return ""
                    elif index.row() == 5:
                        return self.tr("Entry point:")
                    elif index.row() == 6:
                        return self.tr("Exit point:")
                    elif index.row() == 7:
                        return ""
                    elif index.row() == 8:
                        return self.tr("Next:")
                    elif index.row() == 9:
                        return self.tr("Track:")
                    elif index.row() == 10:
                        return self.tr("Arrival time:")
                    elif index.row() == 11:
                        return self.tr("Departure time:")
                elif index.column() == 1:
                    if index.row() == 0:
                        return self._train.serviceCode
                    elif index.row() == 1:
                        return TrainStatus.text(self._train.status)
                    elif index.row() == 2:
                        return self.tr("%3.0d km/h") % \
                            (float(self._train.speed) * 3.6)
                    elif index.row() == 3:
                        return self._train.trainType.description
                    elif index.row() == 4:
                        return ""
                    elif index.row() == 5:
                        return self._train.currentService.entryPlaceName
                    elif index.row() == 6:
                        return self._train.currentService.exitPlaceName
                    elif index.row() == 7:
                        return ""
                    elif index.row() == 8 and line is not None:
                            return line.place.placeName
                    elif index.row() == 9 and line is not None:
                        return line.trackCode
                    elif index.row() == 10 and line is not None:
                        if line.mustStop:
                            return \
                                line.scheduledArrivalTime.toString("hh:mm:ss")
                        else:
                            return self.tr("Non-stop")
                    elif index.row() == 11 and line is not None:
                        return \
                            line.scheduledDepartureTime.toString("hh:mm:ss")
                    else:
                        return ""
            elif role == Qt.ForegroundRole:
                if index.row() == 1 and index.column() == 1:
                    if self._train.status == TrainStatus.RUNNING:
                        return QtGui.QBrush(Qt.darkGreen)
                    elif self._train.status == TrainStatus.STOPPED:
                        return QtGui.QBrush(Qt.darkBlue)
                    elif self._train.status == TrainStatus.WAITING:
                        return QtGui.QBrush(Qt.red)
                    else:
                        return QtGui.QBrush(Qt.darkGray)
                return QtGui.QBrush()
        return None

    def headerData(self, column, orientation, role=Qt.DisplayRole):
        """Returns the headers for this model"""
        if self._train is not None \
           and orientation == Qt.Horizontal \
           and role == Qt.DisplayRole:
            if column == 0:
                return self.tr("Key")
            elif column == 1:
                return self.tr("Value")
            else:
                return ""
        return None

    def flags(self, index):
        """Returns the flags of the model"""
        return Qt.ItemIsEnabled

    @property
    def train(self):
        """Returns the train instance associated with this model"""
        return self._train

    @QtCore.pyqtSlot(int)
    def setTrainByTrainId(self, trainId):
        """Sets the train instance associated with this model from its
        trainId"""
        self.beginResetModel()
        self._train = self.simulation.trains[trainId]
        self.endResetModel()

    @QtCore.pyqtSlot()
    def update(self):
        """Emits the dataChanged signal for the lines that may change."""
        self.dataChanged.emit(self.index(1, 1), self.index(2, 1))
        self.dataChanged.emit(self.index(8, 1), self.index(11, 1))

    @QtCore.pyqtSlot()
    def updateSpeed(self):
        """Emits the dataChanged signal for the speed only."""
        self.dataChanged.emit(self.index(2, 1), self.index(2, 1))


class Train(QtCore.QObject):
    """A ``Train`` is a stock running on a track at a certain speed and to which
       is assigned a :class:`~ts2.trains.service.Service` .
    """

    def __init__(self, parameters):
        """
        :param dict paramaters:
        """
        super().__init__()
        self._parameters = parameters
        self.simulation = None
        self._serviceCode = parameters["serviceCode"]
        self._trainType = None
        self._speed = parameters['speed']
        self._initialSpeed = parameters.get("initialSpeed", 0.0)
        self._accel = 0
        self._trainHead = parameters["trainHead"]
        self._status = parameters.get("status", TrainStatus.INACTIVE)
        self._lastSignal = None
        self._signalActions = [(0, 999)]
        self._applicableActionIndex = 0
        self._actionTime = 0
        self._nextPlaceIndex = None
        self._stoppedTime = 0
        if "stoppedTime" in parameters:
            self._stoppedTime = parameters["stoppedTime"]
        self._minimumStopTime = 0
        self._initialDelayProba = \
            utils.DurationProba(parameters["initialDelay"])
        self._initialDelay = 0
        self._appearTime = QtCore.QTime.fromString(parameters["appearTime"])
        self._shunting = False
        # FIXME Throw back all these actions to MainWindow
        self.assignAction = QtWidgets.QAction(self.tr("Reassign service..."),
                                              self)
        self.assignAction.triggered.connect(self.reassignService)
        self.resetServiceAction = QtWidgets.QAction(self.tr("Reset service"),
                                                    self)
        self.resetServiceAction.triggered.connect(self.resetService)
        self.reverseAction = QtWidgets.QAction(self.tr("Reverse"), self)
        self.reverseAction.triggered.connect(self.reverse)
        self.splitAction = QtWidgets.QAction(self.tr("Split train"), self)
        self.splitAction.triggered.connect(self.splitTrainPopUp)

    def initialize(self, simulation):
        """Initialize the train once everything else is loaded.
        :param simulation: The simulation on which to initialize this Train
        :type simulation: simulation.Simulation"""
        if not self._parameters:
            raise Exception("Internal error: Train already initialized !")
        params = self._parameters
        self.simulation = simulation
        self._trainType = simulation.trainTypes[params["trainTypeCode"]]
        self.trainHead.initialize(simulation)
        if self.simulation.context == utils.Context.GAME:
            if self.currentService is not None:
                self._nextPlaceIndex = params.get('nextPlaceIndex')
            self.setInitialDelay()
            self.updateMinimumStopTime()
            self.activate(simulation.currentTime)

            self.simulation.timeElapsed.connect(self.advance)
            self.simulation.timeChanged.connect(self.activate)
            self.trainStatusChanged.connect(simulation.trainStatusChanged)
            self.trainStoppedAtStation.connect(
                simulation.scorer.trainArrivedAtStation
            )
            self.trainExitedArea.connect(simulation.scorer.trainExitedArea)
            self.reassignServiceRequested.connect(
                simulation.simulationWindow.openReassignServiceWindow
            )
            self.splitTrainRequested.connect(
                simulation.simulationWindow.openSplitTrainWindow
            )
            
            if self.isOnScenery():
                # update the berth on the next signal
                sig = self.findNextSignal()
                if sig is not None:
                    sig.trainId = self.trainId
        self._parameters = None

    def for_json(self):
        """Dumps this train to JSON."""
        if self.simulation.context != utils.Context.GAME or \
                self.status == TrainStatus.INACTIVE:
            speed = self.initialSpeed
            appearTime = self.appearTimeStr
            initialDelay = self.initialDelayStr
        elif self.status == TrainStatus.OUT:
            speed = 0
            appearTime = "00:00:00"
            initialDelay = 0
        else:
            speed = self.speed
            appearTime = self.simulation.currentTime.toString("hh:mm:ss")
            initialDelay = 0
        return {
            "__type__": "Train",
            "trainId": self.trainId,
            "serviceCode": self.serviceCode,
            "trainTypeCode": self.trainTypeCode,
            "status": self.status,
            "speed": speed,
            "initialSpeed": self.initialSpeed,
            "trainHead": self.trainHead,
            "appearTime": appearTime,
            "initialDelay": initialDelay,
            "nextPlaceIndex": self.nextPlaceIndex,
            "stoppedTime": self.stoppedTime
        }

    trainStoppedAtStation = QtCore.pyqtSignal(int)
    trainDepartedFromStation = QtCore.pyqtSignal(int)
    trainStatusChanged = QtCore.pyqtSignal(int)
    trainExitedArea = QtCore.pyqtSignal(int)
    reassignServiceRequested = QtCore.pyqtSignal(int)
    splitTrainRequested = QtCore.pyqtSignal(int)

    # ## Properties ######################################################

    @property
    def trainId(self):
        """Returns the train Id which is index of this train inside the train
        list of the simulation."""
        try:
            trainId = self.simulation.trains.index(self)
        except ValueError:
            trainId = None
        return trainId

    @property
    def initialDelay(self):
        """
        :return: the number of seconds of delay that this train had when it
                 was activated.
        :rtype: int
        """
        return self._initialDelay

    @property
    def minimumStopTime(self):
        """
        :return: the minimum stopping time for next station
        :rtype: int
        """
        return self._minimumStopTime

    @property
    def stoppedTime(self):
        """
        :return: the number of seconds that this train is stopped at then
                 current station.
        :rtype: int
        """
        return self._stoppedTime

    @property
    def serviceCode(self):
        """
        :return: the service code of this train
        :rtype: str
        """
        return self._serviceCode

    @serviceCode.setter
    def serviceCode(self, serviceCode):
        """Changes the train current service code to serviceCode"""
        if serviceCode not in self.simulation.services:
            raise Exception(self.tr("No service with code %s") % serviceCode)
        self._serviceCode = serviceCode
        if self.simulation.context == utils.Context.GAME:
            if self._stoppedTime != 0:
                self.status = TrainStatus.STOPPED
            else:
                self.status = TrainStatus.RUNNING
            self.nextPlaceIndex = 0
            self.drawTrain(0)
            self.findNextSignal().trainId = self.trainId

    @property
    def status(self):
        """
        :return: the status of the train
        :rtype: :class:`~ts2.trains.train.TrainStatus`
        """
        return self._status

    @status.setter
    def status(self, value):
        """Setter function for the status property."""
        oldStatus = self._status
        if self._status == TrainStatus.INACTIVE:
            if value == TrainStatus.RUNNING or value == TrainStatus.STOPPED:
                self._status = value
                self.updateStatus(0)
        elif self._status == TrainStatus.RUNNING:
            if value == TrainStatus.OUT:
                self._speed = 0
                self._status = TrainStatus.OUT
                self.simulation.messageLogger.addMessage(
                    self.tr("Train %s exited the area") % self.serviceCode
                )
            else:
                self._status = value
        else:
            self._status = value
        if self._status != oldStatus:
            self.trainStatusChanged.emit(self.trainId)

    @property
    def currentService(self):
        """Returns the Service object assigned to this train"""
        if self._serviceCode is not None:
            return self.simulation.service(self._serviceCode)

    @property
    def nextPlaceIndex(self):
        """Returns the index of the next place, that is the index of the
        ServiceLine of the current service pointing to the next place the
        train is scheduled to.
        :rtype : int"""
        return self._nextPlaceIndex

    @nextPlaceIndex.setter
    def nextPlaceIndex(self, index):
        """Setter function for the nextPlaceIndex property."""
        if index is None or \
           index < 0 or \
           index >= len(self.currentService.lines):
            self._nextPlaceIndex = None
        else:
            self._nextPlaceIndex = index

    @property
    def trainType(self):
        """
        :return: The TrainType of this Train
        :rtype: :class:`~ts2.trains.traintype.TrainType`
        """
        return self._trainType

    @property
    def trainTypeCode(self):
        """Returns the code of the train type"""
        """
        :return: The code of this trains type
        :rtype: str
        """
        return self._trainType.code

    @trainTypeCode.setter
    def trainTypeCode(self, value):
        """Setter function for the trainTypeCode property"""
        if self.simulation.context == utils.Context.EDITOR_TRAINS:
            try:
                self._trainType = self.simulation.trainTypes[value]
            except KeyError:
                pass

    @property
    def speed(self):
        """Returns the current speed of the Train."""
        return self._speed

    @property
    def signalActions(self):
        """Returns the list of actions asked by the last seen signal. List of
        (target, speed) tuples."""
        return self._signalActions

    @property
    def applicableActionIndex(self):
        """Returns the applicable action in the action list."""
        return self._applicableActionIndex

    @property
    def actionTime(self):
        """
        :return: the time at which the current action has been achieved or 0.
        :rtype: ``QTime`` or 0
        """
        return self._actionTime

    @property
    def initialSpeed(self):
        """Returns the initial speed of the train, i.e. the speed it has when
        it appears on the scene"""
        return self._initialSpeed

    @initialSpeed.setter
    def initialSpeed(self, value):
        """Setter function for the initialSpeed property"""
        if self.simulation.context == utils.Context.EDITOR_TRAINS:
            if value is None or value == "":
                value = "0.0"
            self._initialSpeed = float(value)

    @property
    def trainHead(self):
        """
        :return: the Position of the head of this train.
        :rtype: :class:`~ts2.routing.position.Position`
        """
        return self._trainHead

    @trainHead.setter
    def trainHead(self, value):
        """Setter function for the trainHead property"""
        if self.simulation.context == utils.Context.EDITOR_TRAINS:
            self._trainHead = value

    def _getTrainHeadStr(self):
        """
        :return: the Position of the head of this train.
        :rtype: `str`
        """
        return str(self._trainHead)

    def _setTrainHeadStr(self, value):
        """Setter function for the trainHeadStr property."""
        if self.simulation.context == utils.Context.EDITOR_TRAINS:
            tiId, ptiId, posOnTI = eval(value.strip('()'))
            trackItem = self.simulation.trackItem(tiId)
            previousTI = self.simulation.trackItem(ptiId)
            self.trainHead = position.Position(trackItem, previousTI, posOnTI)

    trainHeadStr = property(_getTrainHeadStr, _setTrainHeadStr)

    @property
    def lastSignal(self):
        """Returns the last signal that the driver has seen, which may be the
        one just in front."""
        return self._lastSignal

    @property
    def initialDelayStr(self):
        """Returns the initialDelay probability function as a string."""
        return str(self._initialDelayProba)

    @initialDelayStr.setter
    def initialDelayStr(self, value):
        """Setter function for the initialDelayStr property."""
        if self.simulation.context == utils.Context.EDITOR_TRAINS:
            self._initialDelayProba = utils.DurationProba(value)

    @property
    def appearTimeStr(self):
        """Returns the time at which this train appears on the scene as a
        String."""
        return self._appearTime.toString("HH:mm:ss")

    @appearTimeStr.setter
    def appearTimeStr(self, value):
        """Setter function for the appearTime property"""
        if self.simulation.context == utils.Context.EDITOR_TRAINS:
            self._appearTime = QtCore.QTime.fromString(value)

    @property
    def shunting(self):
        """
        :return: True if the train is shunting False otherwise
        """
        return self._shunting

    # ## Methods ########################################################

    def isOut(self):
        """
        :return: True if the train exited the area
        :rtype: bool
        """
        return \
            self._trainHead.isOut() and \
            self._trainHead.positionOnTI() > self._trainType.length()

    def isActive(self):
        """
        :return: ``True`` if the train is in the area and its current service
                 is not finished
        :rtype: bool"""
        return \
            self._status != TrainStatus.INACTIVE and \
            self._status != TrainStatus.OUT and \
            self._status != TrainStatus.END_OF_SERVICE

    def isOnScenery(self):
        """
        :return: True if the train is on the scenery
        :rtype: bool
        """
        return \
            self._status != TrainStatus.INACTIVE and \
            self._status != TrainStatus.OUT

    def updateMinimumStopTime(self):
        """Updates the minimum stopping time for next station."""
        self._minimumStopTime = utils.DurationProba(
            self.simulation.option("defaultMinimumStopTime")).yieldValue()

    def showTrainActionsMenu(self, widget, pos):
        """Pops-up the train actions menu on the given QWidget"""
        contextMenu = QtWidgets.QMenu(widget)
        contextMenu.addAction(self.assignAction)
        contextMenu.addAction(self.resetServiceAction)
        contextMenu.addAction(self.reverseAction)
        contextMenu.addAction(self.splitAction)
        contextMenu.exec_(pos)

    def setInitialDelay(self):
        """Sets up the initial delay variable."""
        if self._initialDelayProba.isNull():
            self._initialDelay = utils.DurationProba(
                self.simulation.option("defaultDelayAtEntry")).yieldValue()
        else:
            self._initialDelay = self._initialDelayProba.yieldValue()

    @QtCore.pyqtSlot(float)
    def advance(self, secs):
        """Advances the train by a step corresponding to the elapsed secs,
        and executes all the associated actions."""
        if self.isActive():
            self.updateSignalActions()
            self.setSpeed(secs)
            advanceLength = self._speed * secs
            self._trainHead += advanceLength
            self.updateStatus(secs)
            self.drawTrain(advanceLength)
            self.executeActions(advanceLength)

    @QtCore.pyqtSlot(QtCore.QTime)
    def activate(self, time):
        """Activate this Train if time is after this
        :class:`~ts2.trains.train.Train`'s
        :meth:`~ts2.trains.train.Train.appearTime`.
        """
        if self.status == TrainStatus.INACTIVE:
            realAppearTime = self._appearTime.addSecs(self.initialDelay)
            if self.simulation.startTime.addSecs(-3600) \
                    <= realAppearTime < time:
                self._speed = self._initialSpeed
                # Signals update
                signalAhead = self.findNextSignal()
                if signalAhead is not None:
                    signalAhead.trainId = self.trainId
                signalBehind = self.findPreviousSignal()
                if signalBehind is not None:
                    signalBehind.updateSignalState()
                invertedHead = self._trainHead.reversed()
                oppositeSignalAhead = self.findPreviousSignal(invertedHead)
                if oppositeSignalAhead is not None:
                    oppositeSignalAhead.updateSignalState()
                # Status update
                if self._stoppedTime != 0 or not self.currentService:
                    self.status = TrainStatus.STOPPED
                else:
                    self.status = TrainStatus.RUNNING
                if self.currentService:
                    self.nextPlaceIndex = 0
                self.drawTrain()
                self.executeActions(0)
                # Print messages
                if abs(self.initialDelay) < 60:
                    self.simulation.messageLogger.addMessage(
                        self.tr("Train %s entered the area on time") %
                        self.serviceCode
                    )
                else:
                    loe = self.tr("late") if self.initialDelay > 0 \
                        else self.tr("early")
                    self.simulation.messageLogger.addMessage(
                        self.tr("Train %s entered the area %i minutes %s") %
                        (self.serviceCode, abs(self.initialDelay // 60), loe)
                    )

    @QtCore.pyqtSlot()
    def reverse(self):
        """Reverses the train direction."""
        if self._speed == 0:
            signalAhead = self.findNextSignal()
            if signalAhead is not None:
                signalAhead.resetTrainId()
            activeRoute = self.trainHead.trackItem.activeRoute
            if activeRoute is not None:
                activeRoute.desactivate()
            trainTail = self._trainHead - self._trainType.length
            self._trainHead = trainTail.reversed()
            self._speed = 0
            newSignalAhead = self.findNextSignal()
            if newSignalAhead is not None:
                newSignalAhead.trainId = self.trainId

    @QtCore.pyqtSlot()
    def reassignService(self):
        """ Pops up a dialog for the user to choose the new service and
        reassign it to this train, if the service is not already assigned
        to another train"""
        self.reassignServiceRequested.emit(self.trainId)

    @QtCore.pyqtSlot()
    def resetService(self):
        """Resets the service, i.e. sets the pointer to the first station."""
        if QtWidgets.QMessageBox.question(
                self.simulation.simulationWindow,
                self.tr("Reset a service"),
                self.tr("Are you sure you really "
                        "want to reset service %s?"
                        % self.serviceCode),
                QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel
                ) == QtWidgets.QMessageBox.Ok:
            self.nextPlaceIndex = 0

    @QtCore.pyqtSlot()
    def splitTrainPopUp(self):
        """Pops up a dialog for the user to choose where to split the train and
        then split it."""
        reason = None
        if len(self.trainType.elements) < 2:
            reason = self.tr("This train cannot be split")
        if self.speed != 0:
            reason = self.tr("This train is not stopped")
        if reason:
            QtWidgets.QMessageBox.warning(
                self.simulation.simulationWindow,
                self.tr("Unable to split train"),
                reason,
                QtWidgets.QMessageBox.Ok
            )
        else:
            self.splitTrainRequested.emit(self.trainId)

    def splitTrain(self, splitIndex):
        """Splits this train at the given index.
        :param splitIndex: The index at which to split the train. 1 is between
        the first and second element, 2 between the second and third, etc.
        counting from the train head."""
        headElements = self.trainType.elements[:splitIndex]
        tailElements = self.trainType.elements[splitIndex:]
        headTrainType = None
        tailTrainType = None
        for trainType in self.simulation.trainTypes.values():
            if headElements == trainType.elements or \
                    (len(headElements) == 1 and
                     headElements[0] == trainType):
                headTrainType = trainType
            if tailElements == trainType.elements or \
                    (len(tailElements) == 1 and
                     tailElements[0] == trainType):
                tailTrainType = trainType
            if headTrainType and tailTrainType:
                break

        # Check if there exists a new train type for the head and tail trains
        if not headTrainType or not tailTrainType:
            QtWidgets.QMessageBox.warning(
                self.simulation.simulationWindow,
                self.tr("Unable to split train"),
                self.tr("This train cannot be split"),
                QtWidgets.QMessageBox.Ok
            )
            return
        # Change our own train type to the head type
        self._trainType = headTrainType
        # Create a new train for the tail
        parameters = {
            "__type__": "Train",
            "serviceCode": None,
            "trainTypeCode": tailTrainType.code,
            "status": TrainStatus.INACTIVE,
            "speed": 0.0,
            "initialSpeed": 0.0,
            "trainHead": self.trainHead - headTrainType.length - 1.0,
            "appearTime": self.simulation.currentTime.toString(),
            "initialDelay": 0,
            "nextPlaceIndex": None,
            "stoppedTime": 1.0
        }
        newTrain = Train(parameters)
        self.simulation.addTrain(newTrain)
        newTrain.initialize(self.simulation)
        newTrain.reassignService()

    def jumpToNextPlace(self):
        """Set the nextPlaceIndex to the next serviceLine. If there is no
        serviceLine after the current one, change the service of the train to
        nextService if any."""
        self.updateMinimumStopTime()
        if self.nextPlaceIndex == len(self.currentService.lines) - 1:
            # The service is ended
            if self.currentService.autoReverse:
                self.reverse()
            if self.currentService.nextServiceCode != "":
                self.serviceCode = self.currentService.nextServiceCode
            else:
                self.nextPlaceIndex = None
        else:
            self.nextPlaceIndex += 1

    def updateSignalActions(self):
        """Updates the applicable signal actions list based on the position
        of the train and the visible signal."""
        nsp, nsd = self.getNextSignalInfo()
        if nsp.isNull():
            # No more signal ahead
            self._signalActions = [(0, 999)]
            self._applicableActionIndex = 0
            return
        signalVisibility = float(
            self.simulation.option("defaultSignalVisibility")
        )
        if nsd < signalVisibility:
            # We can see the next signal aspect
            if nsp.trackItem.activeAspect.actions:
                # It requires actions
                # We check actions each time because the aspect of the signal
                # might have changed
                self._signalActions = nsp.trackItem.activeAspect.actions
                if self.lastSignal != nsp.trackItem:
                    # We see this signal for the first time
                    self._lastSignal = nsp.trackItem
                    self._applicableActionIndex = 0
                    self._actionTime = 0
            else:
                # This signal does not require actions, so we only update our
                # memory of the last signal
                self._lastSignal = nsp.trackItem

        applicableAction = self.signalActions[self.applicableActionIndex]
        currentTime = self.simulation.currentTime
        if abs(self.speed - applicableAction[1]) < 0.1:
            # We have achieved the target speed
            if self._actionTime == 0:
                self._actionTime = currentTime
            if len(applicableAction) >= 3:
                timeToWait = applicableAction[2]
            else:
                timeToWait = 0
            if currentTime > self._actionTime.addSecs(timeToWait):
                # We have waited enough, so we go to next action
                if len(self.signalActions) > self.applicableActionIndex + 1:
                    self._applicableActionIndex += 1

    def executeActions(self, advanceLength):
        """ Execute actions that have to be done when the train head enters
        a trackItem or when the train tail leaves another.
        For each case this is done in two stages:
        - first execute actions related to the train itself and
        - then call TrackItem.trainHeadActions() or
        TrackItem.trainTailActions())."""
        # Train head
        trainExiting = False
        oth = self._trainHead - advanceLength
        for ti in oth.trackItemsToPosition(self._trainHead):
            if isinstance(ti, lineitem.LineItem):
                if ti.placeCode is not None and ti.placeCode != "":
                    if self.currentService is not None and \
                       self.nextPlaceIndex is not None:
                        line = self.currentService.lines[self.nextPlaceIndex]
                        if line.placeCode == ti.placeCode:
                            # We are at the nextPlace
                            if not line.mustStop:
                                # Train does not stop at this place
                                self.jumpToNextPlace()
                                self.trainStatusChanged.emit(self.trainId)
            if self.isActive():
                ti.trainHeadActions(self.trainId)
        if self._trainHead.isOut():
            trainExiting = True
        # Train tail
        tt = self._trainHead - self._trainType.length
        ott = tt - advanceLength
        for ti in ott.trackItemsToPosition(tt):
            if self.isActive():
                ti.trainTailActions(self.trainId)
        if tt.isOut() and trainExiting:
            self.status = TrainStatus.OUT
            self.trainExitedArea.emit(self.trainId)

    def updateStatus(self, secs):
        """Updates the status of the train"""
        if not self.isActive():
            return
        if self._speed > 0.25:
            # Speed is not null, the train is running
            self.status = TrainStatus.RUNNING
        else:
            if self.currentService is not None and \
               self.nextPlaceIndex is not None:
                # The train is operating on a service that is not over
                line = self.currentService.lines[self.nextPlaceIndex]
                trainHeadItem = self._trainHead.trackItem
                if isinstance(trainHeadItem, lineitem.LineItem) \
                        and trainHeadItem.placeCode == line.placeCode:
                    # Train is stopped at the scheduled nextStop place
                    if self.status == TrainStatus.RUNNING:
                        # Train just stopped
                        self.status = TrainStatus.STOPPED
                        self._stoppedTime = 0
                        self.trainStoppedAtStation.emit(self.trainId)
                    elif self.status == TrainStatus.STOPPED:
                        # Train is already stopped at the place
                        if line.scheduledDepartureTime > \
                                self.simulation.currentTime or \
                                self._stoppedTime < self.minimumStopTime or \
                                line.scheduledDepartureTime == QtCore.QTime():
                            # Conditions to depart are not met
                            self.status = TrainStatus.STOPPED
                            self._stoppedTime += secs
                        else:
                            # Train departs
                            oldService = self.currentService
                            self.jumpToNextPlace()
                            if self.currentService != oldService:
                                # The service code has changed
                                if self._trainHead.trackItem.placeCode == \
                                        self.currentService.lines[
                                        self.nextPlaceIndex].placeCode:
                                    # This is also the first scheduled place
                                    # of the new service
                                    self.status = TrainStatus.STOPPED
                                else:
                                    # The first scheduled place of this new
                                    # service is not here
                                    self.status = TrainStatus.RUNNING
                                    self.trainDepartedFromStation.emit(
                                        self.trainId
                                    )
                            elif self.nextPlaceIndex is not None:
                                # There are still places to call at
                                self.status = TrainStatus.RUNNING
                                self.trainDepartedFromStation.emit(
                                    self.trainId
                                )
                            else:
                                # There was the last place to call at
                                self.status = TrainStatus.END_OF_SERVICE
                else:
                    # Train is stopped but not at a scheduled station
                    self.status = TrainStatus.WAITING
            else:
                # Train is stopped but not assigned any service
                self.status = TrainStatus.WAITING

    def drawTrain(self, advanceLength=0):
        """This function draws the train on the scene by setting the correct
        trainHead and trainTail to the different trackItems met.

        :param advanceLength : The length that the train has advanced since
        the last call to this function."""
        trainTail = self.trainHead - self.trainType.length
        oldTrainTail = trainTail - advanceLength
        # Register train on new items (even if to be unregistered just behind)
        for ti in trainTail.trackItemsToPosition(self.trainHead):
            ti.registerTrain(self)
        # Unregister train on left behind items:
        for ti in oldTrainTail.trackItemsToPosition(trainTail):
            if ti != trainTail.trackItem:
                ti.unRegisterTrain(self)
        # Update head and tails for all
        for ti in oldTrainTail.trackItemsToPosition(self.trainHead):
            ti.updateTrainHeadAndTail()

    def getNextSignalInfo(self, pos=None):
        """
        :param pos:
        :type pos: :class:`~ts2.routing.position.Position`
        :return: - the position and distance of first signal ahead of the train
                   head
                 - or ahead of the given position if specified
        :rtype: (:class:`~ts2.routing.position.Position`, int)
        """
        if pos is None:
            pos = position.Position()
        retPos = position.Position()
        retDist = -1
        if pos == position.Position():
            pos = self._trainHead
        if not isinstance(pos.trackItem, enditem.EndItem):
            cur = pos.next()
            while not isinstance(cur.trackItem, enditem.EndItem):
                ti = cur.trackItem
                if isinstance(ti, signalitem.SignalItem):
                    if ti.isOnPosition(cur):
                        retPos = cur
                        break
                cur = cur.next()
        if retPos != position.Position():
            retDist = self._trainHead.distanceToPosition(retPos)
        return retPos, retDist

    def findNextSignal(self, pos=position.Position()):
        """ @return The first signal ahead the train head
        or ahead of the given position if specified"""
        nsp, nsd = self.getNextSignalInfo(pos)
        return nsp.trackItem

    def getDistanceToNextSignal(self, pos=position.Position()):
        """Returns the distance to the next Signal"""
        nsp, nsd = self.getNextSignalInfo(pos)
        return nsd

    def findPreviousSignalPosition(self, pos=position.Position()):
        """ Finds the position of the first signal behind the train head or
        the given position.
        @return The position of the first signal behind"""
        if pos == position.Position():
            cur = self._trainHead
        else:
            cur = pos
        while not isinstance(cur.trackItem, enditem.EndItem):
            ti = cur.trackItem
            if isinstance(ti, signalitem.SignalItem):
                if ti.isOnPosition(cur):
                    return cur
            cur = cur.previous()
        return position.Position()

    def findPreviousSignal(self, pos=position.Position()):
        """ @return The first signal behind the train head"""
        return self.findPreviousSignalPosition(pos).trackItem

    def getDistanceToNextStop(self, maxDistance):
        """Returns the distance to the next stop by looking forward of
        the _trainHead up to a maximum distance of maxDistance."""
        if self.currentService is None or \
           self.nextPlaceIndex is None:
            # No service assigned or no more place to call at
            return -1
        for i in range(self.nextPlaceIndex, len(self.currentService.lines)):
            line = self.currentService.lines[i]
            if line.mustStop:
                break
        else:
            return -1
        pos = self._trainHead
        distance = pos.trackItem.realLength - self._trainHead.positionOnTI
        while (not isinstance(pos.trackItem, enditem.EndItem) and
                (distance < maxDistance)):
            ti = pos.trackItem
            if isinstance(ti, signalitem.SignalItem):
                if ti.isOnPosition(pos) and \
                   ti.activeAspect.meansProceed():
                    # We have a red signal here, no need to go further
                    return -1
            if ti.place == line.place:
                return distance
            pos = pos.next()
            distance += pos.trackItem.realLength
        return -1

    def getDistanceToNextTrain(self, maxDistance, trackCircuit=False):
        """Returns the distance to the next train by looking forward of
        the _trainHead up to a maximum distance of maxDistance. If
        trackCircuit is True, then the distance is given to the trackItem on
        which a train is present. Otherwise, the real distance to the train is
        returned."""
        pos = self.trainHead
        distance = 0
        while (pos.isValid() and
               (not isinstance(pos.trackItem, enditem.EndItem) and
               (distance < maxDistance))):
            ti = pos.trackItem
            if isinstance(ti, signalitem.SignalItem):
                if ti.isOnPosition(pos) and \
                   not ti.activeAspect.meansProceed():
                    # We have a red signal here, no need to go further
                    return -1
            distanceToTrain = ti.distanceToTrainEnd(pos)
            if distanceToTrain != -1:
                if trackCircuit:
                    return distance
                else:
                    return distance + distanceToTrain
            pos = pos.next()
            if distance:
                distance += ti.realLength
            else:
                distance = ti.realLength - self.trainHead.positionOnTI
        return -1

    def getNextSpeedLimitInfo(self, maxDistance):
        """
        :param int maxDistance: The maximum distance to look ahead
        :return: the next speed limit and the distance at which it starts,
                 looking at each trackitem forward of the trainHead up to a
                 maximum distance of ``maxDistance``.
        :rtype: (int, ?)
        """
        pos = self._trainHead
        distance = pos.trackItem.realLength - self._trainHead.positionOnTI
        while (not isinstance(pos.trackItem, enditem.EndItem) and
               distance < maxDistance):
            pos = pos.next()
            ti = pos.trackItem
            if ti.maxSpeed < self.getMaximumSpeed() - self.trainType.stdBraking:
                return ti.maxSpeed, distance
            distance += ti.realLength
        return self.getMaximumSpeed(), -1

    def setSpeed(self, secs):
        """Sets the speed of the train.

        :param: secs: Number of seconds (in the game) between two clock
        ticks.
        """
        if not self.isActive() or self.status == TrainStatus.STOPPED:
            self._speed = 0
            return

        # k is the gain factor to set acceleration from the difference
        # between current speed and target speed
        k = 1 / secs

        # ====== Get distances to next targets =======
        # Next Signal
        applicableAction = self.signalActions[self.applicableActionIndex]
        nsp, distanceToNextSignal = self.getNextSignalInfo()
        if applicableAction[0] == signalaspect.Target.ASAP:
            # We emulate a distance to next signal to get a stdBraking
            distanceToNextSignal = (
                ((self.speed - self.trainType.stdBraking * secs)**2 -
                 applicableAction[1]**2) / (2 * self.trainType.stdBraking) +
                (self.speed * secs / 2)
            )
        if applicableAction[0] == signalaspect.Target.BEFORE_NEXT_SIGNAL:
            if nsp.trackItem == self.lastSignal:
                # The signal with the applicable action is still ahead
                distanceToNextSignal += self.getDistanceToNextSignal(nsp)

        # Next station
        maxDistance = max(self._speed**2 / self._trainType.stdBraking, 50.0)
        distanceToNextStation = self.getDistanceToNextStop(maxDistance)

        # Next speed limit
        nextSpeedLimit, distanceToNextLimit = self.getNextSpeedLimitInfo(
            maxDistance
        )

        # Next train
        safetyDistance = 0.0 if self.shunting else 100.0
        distanceToNextTrain = self.getDistanceToNextTrain(maxDistance)
        if distanceToNextTrain != -1:
            distanceToNextTrain -= safetyDistance

        # ====== Calculate speeds to manage each target ======
        # Next signal
        if applicableAction[0] == signalaspect.Target.BEFORE_THIS_SIGNAL \
                and nsp.trackItem != self.lastSignal:
            # We passed the signal, and we keep its speed limit until we
            # see the next one.
            targetSpeedForSignal = applicableAction[1]
        else:
            targetSpeedForSignal = self.targetSpeed(secs, distanceToNextSignal,
                                                    applicableAction[1])
        # Next station
        targetSpeedForStation = self.targetSpeed(secs, distanceToNextStation, 0)

        # Next speed limit
        targetSpeedForLimit = self.targetSpeed(secs, distanceToNextLimit,
                                               nextSpeedLimit)

        # Next train
        targetSpeedForTrain = self.targetSpeed(secs, distanceToNextTrain, 0)

        ts = min(targetSpeedForSignal,
                 targetSpeedForStation,
                 targetSpeedForLimit,
                 targetSpeedForTrain)
        self._accel = max(-self._trainType.emergBraking,
                          min(k * (ts - self._speed),
                              self._trainType.stdAccel))
        self._speed = max(0.0, self._speed + self._accel * secs)

        # ### DEBUG ###
        # print("SC:%s, Secs:%f, Accel=%f; ts=%f, speed=%f,"
        # "dtnStation:%f, dtnSignal:%f, dtnLimit:%f, dtnTrain:%f,
        # appl.action=%s" % (self.serviceCode, secs, self._accel, ts,
        # self._speed, distanceToNextStation, distanceToNextSignal,
        # distanceToNextLimit, distanceToNextTrain, str(applicableAction)))

    def targetSpeed(self, secs, targetDistance=-1, targetSpeedAtPos=0):
        """Defines the current target speed of the train depending on the
        parameters.

        :param targetDistance: the distance at which the train should be at
               targetSpeedAtPos
        :param targetSpeedAtPos: the target speed when the train will be at
               targetDistance
        :return: the current target speed for the train, including sampling
                 margin.
        :rtype: `float`
        """
        maxSpeed = self.getMaximumSpeed()
        # d is the maximum distance that can be travelled during the last
        # sample. It is used to determine when to stop the train.
        d = 0.5 * self.trainType.stdBraking * secs**2

        if targetDistance == -1:
            return maxSpeed
        if targetDistance < d:
            return targetSpeedAtPos

        theoreticalSpeed = self.calculatedSpeed(targetDistance,
                                                targetSpeedAtPos)
        # s1 is half the distance run at the train's current speed during secs
        # This value is used to get a centered sampling of the braking curve.
        s1 = self._speed * secs / 2
        # s2 is equivalent to s1, but taking into account the theoreticalSpeed
        s2 = theoreticalSpeed * secs / 2
        if theoreticalSpeed < self._speed:
            return self.calculatedSpeed(targetDistance - s1,
                                        targetSpeedAtPos)
        else:
            return self.calculatedSpeed(targetDistance - s2,
                                        targetSpeedAtPos)

    def calculatedSpeed(self, targetDistance, targetSpeedAtPos):
        """Returns the speed the train should be right now to be able to be
        at a speed of targetSpeedAtPos at a distance of targetDistance from
        the train head, not exceeding maxSpeed. This function does not take
        into account any sampling margin."""
        return min(self.getMaximumSpeed(),
                   sqrt(abs(2 * targetDistance * self._trainType.stdBraking) +
                        targetSpeedAtPos**2))

    def getMaximumSpeed(self):
        """Returns the maximum speed allowed for the train in its current
        position"""
        return min(self._trainType.maxSpeed,
                   self.trainHead.trackItem.maxSpeed)
