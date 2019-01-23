from .global_info import GlobalInfo


class LowLevelModule:
    def __init__(self, global_info: GlobalInfo):
        self.global_info = global_info

    @property
    def sc2_env(self):
        return self.global_info.sc2_env

    @property
    def logger(self):
        return self.global_info
