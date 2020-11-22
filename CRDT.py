from random import randint

class Character:
    pass

class CRDT_DOC:
    def __init__(self, file_path = None, siteID = 0, id_bound = 10, base_range = 16):
        self.siteID = siteID
        self._id_strategy = {}
        self._id_boundary = 10
        self._base_range = base_range
        self._chars = self._from_file() if file_path else []

    def _from_file(self):
        return []
    
    def generatePosBetween(self, pos1, pos2, depth = 0, newPos=[], is_root = True):
        id1 = pos1[depth]
        id2 = pos2[depth]
        alloc_strategy = self._get_strategy(depth)

        if (id2 - id1 > 1):
            newDigit = self.generateIdBetween(id1, id2, depth)
            newPos.append(newDigit)
            return newPos

        elif (id2 - id1 == 1):
            if len(pos1) != depth:
                if alloc_strategy == "+":
                    newPos.append(id1)
                    return self.generatePosBetween(pos1, pos2, depth + 1, newPos)
                else:
                    newPos.append(id2)
                    return self.generatePosBetween(pos1, pos2, depth + 1, newPos)
            else:
                # TODO: create new depth

                pass
    
    def generateIdBetween(self, id1, id2, depth):
        strategy  = self._get_strategy(depth)
        step = id2 - id1
        new_id = None

        if strategy == "+":
            if step < self._id_boundary:
                new_id = id1 + randint(1, self._id_boundary)
            else:
                new_id = id1 + randint(1, step)
        else:
            if step < self._id_boundary:
                new_id = id2 - randint(1, self._id_boundary)
            else:
                new_id = id2 - randint(1, step)

        return new_id

    def _get_strategy(self, depth):
        if depth not in self._id_strategy:
            self._id_strategy[depth] = "+" if randint(0, 2) == 0 else "-" 
        
        return self._id_strategy[depth]

    def newID(self, digit):
        pass

if __name__ == "__main__":
    # For unit tests
    pass


# Unique id allocation - incomplete - based on LSEQ paper

# def alloc_id(self, leftID, rightID):
#     depth = 0
#     interval = 0

#     while interval < 1:
#         depth += 1
#         interval = self.prefix(rightID, depth) - self.prefix(leftID, depth) - 1
    
#     step = min (self._id_boundary, interval)

#     if depth not in self._id_strategy:
#         self._id_strategy[depth] = "+" if randint(0, 2) == 0 else "-" 

#     if self._id_strategy[depth] == "+":
#         new_id = self.prefix(leftID, depth) + randint(0, step) + 1
#     else:
#         new_id = self.prefix(rightID, depth) - (randint(0, step) + 1)
    
#     return new_id

# def prefix(self, _id, depth):
#     idCopy = []

#     for level in range(1, depth):
#         if level < len(_id):
#             idCopy.append()
#         else:
#             pass
#     return 0