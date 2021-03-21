from random import randint
from sortedcontainers import SortedList, SortedDict
import json
import re

ALL_REGEX = re.compile("[a-zA-Z0-9 ./<>?;:\"\'`!@#$%^&*()\[\]\{\}_+=|(\\)-,~]%[0-9]")
SEP = "\n---------------------------------------------\n"

class Character:
    def __init__(self, val, pos, author):
        self._val = val
        self._pos = pos
        self._author = author
    
    @classmethod
    def from_pos(cls, val, pos):
        return Character(val, pos[:-2], pos[-1])

    def pos(self):
        return pos

    def author(self):
        return self._author

    def __lt__(self, other):
        if self._pos == None or other._pos == None:
            raise Exception("Can not compare uninitialized variables\t lvalue" + str(self) + "\trvalue: " + str(other))
        
        return self._pos + [self._author, ] < other._pos + [other._author, ]
    
    def __str__(self):
        return self._val
    
    def to_json(self):
        return json.dumps({"val": self._val,
                            "id" : self._pos,
                            "auth" :  self._author})

class CRDT_DOC:
    def __init__(self, file_path = None, siteID = 0, id_bound = 10, base_range = 4):
        self.siteID = siteID
        self._id_strategy = {}
        self._id_boundary = 10
        self._base_range = base_range
        self._chars = self._from_file(file_path) if file_path else SortedList()

        if file_path == None:
            self._chars.add(Character("", [0, ], self.siteID))
            self._chars.add(Character("", [2 ** self._base_range - 1, ], self.siteID))

    def _from_file(self, file_path):
        doc = SortedList()
        with open(file_path) as file:
            whole_file = file.read()

            empty_start = Character("", [0, ], self.siteID)
            empty_end = Character("", [2 ** self._base_range - 1], self.siteID)

            doc.add(empty_start)
            doc.add(empty_end)
            for char in whole_file:
                self.insert_local(char, empty_start._pos, empty_end._pos)
        return doc

    def insert_local(self, val, pred_char, succ_char):
        new_pos = self.generatePosBetween(pred_char._pos, succ_char._pos)
        new_char = Character(val, new_pos, self.siteID)
        print("Inserted char:", val, "\tposition:", new_pos)
        self._chars.add(new_char)

    def generatePosBetween(self, pos1, pos2, depth = 0, newPos=[], is_root = True):
        id1 = pos1[depth]
        id2 = pos2[depth]
        alloc_strategy = self._get_strategy(depth)

        if (id2 - id1 > 1):
            newDigit = self.generatePosInLevel(id1, id2, depth)
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
                breadth = 2 ** (self._base_range + depth)
                new_digit = self.generatePosInLevel(newPos.append(0), newPos.append(breadth - 1), depth + 1)
                return newPos.append(new_digit)
    
    def generatePosInLevel(self, id1, id2, depth):
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
    
    def __str__(self):
        ret = self.printState()

        for i in self._chars:
            ret += str(i)

        return ret + SEP
    
    def __getitem__(self, key):
        return self._chars[key]
    
    def printState(self):
        char_count = len(self._chars)
        if char_count > 0:
            min_id = self._chars[0]._pos
            max_id = self._chars[-1]._pos
        
        ret = SEP + \
              "char count: " + str(char_count)
        
        if char_count > 0:
            ret += "\n" + \
                "min position: " + str(min_id) + "\n" + \
                "max position: " + str(max_id)
        ret += SEP

        return ret

if __name__ == "__main__":
    # For unit tests
    print("CRDT single write test")
    doc = CRDT_DOC()
    print(doc.printState())

    while True:
        usr_input = input("insert char%pos or \"show\" or \"status\" or \"end\": ")
        if usr_input == "status":
            print(doc.printState())
            continue
        elif usr_input == "show":
            print(doc)
            continue
        elif usr_input == "end":
            print("Final state:\n", doc)
            break
        elif ALL_REGEX:        
            usr_input = usr_input.split("%")
            char = usr_input[0]
            pos = int(usr_input[1])

            doc.insert_local(char, doc[pos - 1], doc[pos])
            print("inserted")
        else:
            print("skipped")




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