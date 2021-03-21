
def file_reader(path):
    if path.find(".py") == -1:
        raise "err"

    file = open(path, "r").read()

    i = 0
    for char in file:
        print(char, "at pos", i)
        i += 1

file_reader("test.py")