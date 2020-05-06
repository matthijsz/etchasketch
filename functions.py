from pointerclass import *


def Reformat_image(img_path):
    img = cv2.bitwise_not(cv2.imread(img_path, 0)) // 255
    img = np.insert(img, 0, 0, axis=1)
    img = np.insert(img, 0, 0, axis=0)
    img = np.insert(img, img.shape[0], 0, axis=0)
    img = np.insert(img, img.shape[1], 0, axis=1)
    return img


# Get sign function for directions. returns either -1, 0, or 1, depending on the polarity of x
def get_sign(x):
    if (x > 0):
        return (1)
    elif (x < 0):
        return (-1)
    else:
        return (0)


# If there's a lot of coords to return to, find the best order to visit them in
def find_best_order(current_x, current_y, coordstovisit):
    coordstovisit += [[current_x, current_y]]
    dist_matrix = cdist(coordstovisit, coordstovisit)
    ccol = dist_matrix[:, -1:]
    ccolmin = ccol[np.nonzero(ccol)].min()
    minindex = np.where(ccol == ccolmin)[0][0]
    order = [coordstovisit[minindex]]
    dist_matrix[:, dist_matrix.shape[0] - 1] = 0
    dist_matrix[dist_matrix.shape[0] - 1, :] = 0
    for i in range(len(coordstovisit) - 2):
        ccol = dist_matrix[:, minindex]
        ccolmin = ccol[np.nonzero(ccol)].min()
        previous_min = minindex
        minindex = np.where(ccol == ccolmin)[0][0]
        order += [coordstovisit[minindex]]
        dist_matrix[:, previous_min] = 0
        dist_matrix[previous_min, :] = 0
    return order


def find_adjecent_ones(x, y, history, img_):
    ones, vh, diag = {}, [], []
    for i in [-1, 1]:
        if img_[y, x + i] == 1:
            vh += [[x + i, y]]
        if img_[y + i, x] == 1:
            vh += [[x, y + i]]
    for ix in [-1, 1]:
        for iy in [-1, 1]:
            if not (ix == 0 and iy == 0):
                if img_[y + iy, x + ix] == 1:
                    diag += [[x + ix, y + iy]]
    vh = [x for x in vh if x not in history]
    diag = [x for x in diag if x not in history]
    ones['vh'], ones['diag'] = vh, diag
    return (ones)


# Create graph (node-dictionary) to use in bfs
def Create_graph2(img, visited=False):
    if not np.all(visited):
        coords_1 = np.transpose(np.where(img == 1))
    else:
        img[np.where(visited == 1)] = 1
        coords_1 = np.transpose(np.where(img == 1))
    Graph = {}
    for I in coords_1:
        i = tuple([I[1], I[0]])
        adjecents = []
        for ix in [-1, 0, 1]:
            x_2 = i[0] + ix
            for iy in [-1, 0, 1]:
                y_2 = i[1] + iy
                if img[y_2][x_2] == 1:
                    adjecents += [(x_2, y_2)]
        adjecents = [x for x in adjecents if x != i]
        Graph[i] = adjecents
    return Graph


# Use breadth first search to find the shortest path from start to any goal given Graph of visited nodes/pixels
def bfs_shortest_path_goallist(graph, start, goals):
    explored = []
    queue = [[start]]
    for i in range(len(graph)):  # At worst walk over all graphs in the node
        try:
            path = queue.pop(0)
        except IndexError:
            return False
        node = path[-1]
        if node not in explored:
            neighbours = graph[node]
            for neighbour in neighbours:
                new_path = list(path)
                new_path.append(neighbour)
                queue.append(new_path)
                if neighbour in goals:
                    return new_path
            explored.append(node)
    return False


# Create graph (node-dictionary) to use in bfs
def Create_graph_visited(x, y, history, visited):
    history_tup = [tuple(x) for x in history] + [(x, y)]
    history_tup = list(set(history_tup))
    Graph = {}
    for i in history_tup:
        adjecents = []
        for ix in [-1, 0, 1]:
            x_2 = i[0] + ix
            for iy in [-1, 0, 1]:
                y_2 = i[1] + iy
                if visited[y_2][x_2] == 1:
                    adjecents += [(x_2, y_2)]
        adjecents = [x for x in adjecents if x != i]
        Graph[i] = adjecents
    return Graph


# Find nearest black pixels when starting, regardless of zeros
def find_nearest_one(img, x_, y_):
    start_coords = np.array([[x_], [y_]])
    not_visited_coords = np.array(np.where(img == 1))
    distance_matrix = cdist(np.transpose(start_coords), np.transpose(not_visited_coords), metric='chebyshev')
    min_distance = distance_matrix.min()
    best_path_index = np.array(np.where(distance_matrix == min_distance))[:, 0]
    nearest_one = not_visited_coords[:, best_path_index[1]]
    return ([nearest_one[1], nearest_one[0]])


def my_distance(i, not_visited_coords, visited_coords):  # To deal with memory issues
    # print(str(i),end='\r')
    vis_y = visited_coords[0, :]
    vis_x = visited_coords[1, :]
    nvis_y = np.repeat(not_visited_coords[0, i], len(vis_y))
    nvis_x = np.repeat(not_visited_coords[1, i], len(vis_y))

    c = np.maximum(abs(nvis_y - vis_y), abs(nvis_x - vis_x))
    overall_min = c.min()
    min_index = np.where(c == c.min())[0][0]
    old_coords = [vis_x[min_index], vis_y[min_index]]
    new_coords = [nvis_x[min_index], nvis_y[min_index]]
    return [overall_min, old_coords, new_coords]
