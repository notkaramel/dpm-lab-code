from abc import ABC, abstractmethod


class _State(ABC):
    def __init__(self, statemachine):
        self.statemachine = statemachine
        self.init()

    @property
    def current_state(self):
        return self.statemachine.current_state

    def transition(self, stateClass):
        self.statemachine.transition(stateClass)

    @abstractmethod
    def init(self):
        pass

    @abstractmethod
    def enter(self):
        pass

    @abstractmethod
    def exit(self):
        pass

    @abstractmethod
    def action(self):
        pass


class StateMachine:
    def _enter(self, stateClass: type):
        """Enter the given class and make it the current state"""
        if not isinstance(stateClass, type) or not issubclass(stateClass, _State):
            raise RuntimeError("You should provide a subclass of State")

        stateObj: _State = self._states[stateClass]
        self._current_state = stateClass
        stateObj.enter()

    def _exit(self):
        """Exits the current state"""
        if not isinstance(self._current_state, type) or not issubclass(self._current_state, _State):
            raise RuntimeError("Current state is invalid, cannot exit")

        stateObj: _State = self._states[self._current_state]
        stateObj.exit()

    @property
    def current_state(self):
        return self._current_state.__qualname__

    def transition(self, stateClass: type):
        """Exits the current state, and enters the given state"""
        self._exit()
        self._enter(stateClass)

    def update(self):
        """Performs the action of the current state"""
        if isinstance(self._current_state, type) and self._current_state is not None:
            self.start()
            stateObj: _State = self._states[self._current_state]
            stateObj.action()

    def start(self):
        if not self._is_started:
            self._enter(self._current_state)
            self._is_started = True

    def __init__(self, initialStateClass: _State):
        """Must provide an initialStateClass that is an attribute of this StateMachine class."""
        self._states = {}

        for attr, value in self.__class__.__dict__.items():
            if isinstance(value, type) and issubclass(value, _State):
                self._states[value] = value(self)

        if initialStateClass not in self._states:
            raise RuntimeError("StateMachine needs a valid initial state")

        self._current_state = initialStateClass
        self._is_started = False


class State(_State):
    def init(self):
        pass

    def enter(self):
        pass

    def exit(self):
        pass

    def action(self):
        pass


if __name__ == '__main__':
    import time

    class MyMachine(StateMachine):
        class IDLE(State):
            def init(self):
                self.start_time = None

            def enter(self):
                self.start_time = time.time()

            def action(self):
                print("nothing", time.time() - self.start_time)
                if time.time() - self.start_time > 3:
                    self.transition(MyMachine.DOING)

            def exit(self):
                print("leaving to do something!\n")

        class DOING(State):
            def init(self):
                self.start_time = None

            def enter(self):
                self.start_time = time.time()

            def action(self):
                print("yay! let's go!", time.time() - self.start_time)
                if time.time() - self.start_time > 5:
                    self.transition(MyMachine.IDLE)

            def exit(self):
                print("going to do nothing!\n")

    machine = MyMachine(MyMachine.IDLE)

    while True:
        time.sleep(1)
        machine.update()
        print(machine.current_state)
