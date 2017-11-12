
node_space = {}


def get_node_name(node):
    class_name = node.__class__.__name__
    index = 0
    while True:
        name = class_name.lower() + '_' + str(index)
        if name in node_space:
            index += 1
        else:
            return name


def get_node(name):
    return node_space.get(name, None)


def flush():
    node_space = {}
