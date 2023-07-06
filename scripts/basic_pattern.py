class BasicPattern:
    def __init__(self, loop_list, delta_list, whorl_list):
        self.loop_list = loop_list
        self.delta_list = delta_list
        self.whorl_list = whorl_list

    def get_type_of_basic_pattern(self):
        if len(self.loop_list) > 2 :
            return "whorl"
        elif len(self.loop_list) == 1 or len(self.loop_list) == 2:
            return "loop"
        elif len(self.loop_list) == 0 and len(self.delta_list) == 0 and len(self.whorl_list) == 0:
            return "arch"