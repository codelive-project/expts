BASE_BITS = 5

class Position:
    def __init__(self, pos_array, pos_num = 0, author = -1):
        self.pos_num = 0
        self.pos = [] if pos_array == None else pos_array
        self.author = author

    @classmethod
    def new_position(cls, pred, succ):
        pass
    
    def pos_at_level(self, depth):
        
        return 

