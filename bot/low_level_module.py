from .hypervisor import Hypervisor


class LowLevelModule:
    def __init__(self, hypervisor: Hypervisor):
        self.hypervisor = hypervisor

    @property
    def sc2_env(self):
        return self.hypervisor.sc2_env

    @property
    def logger(self):
        return self.hypervisor.logger
