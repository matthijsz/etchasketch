import cv2, random, time, imageio,os, argparse, datetime, multiprocessing, tkinter
import numpy as np
from PIL import Image
from scipy.spatial.distance import cdist
import PIL.Image, PIL.ImageTk
from tkinter import filedialog
from joblib import Parallel, delayed
from my_gui import *
from Google_Image import *
from pointerclass import *
from functions import *
from Astar import *
#Find the middle of the image
class start:
    def __init__(self,img,method='topleft'):
        if method=='middle':
            self.x=int(len(img[0])/2)
            self.y=int(len(img)/2)
        if method.endswith('left'):
            self.x=int(1)
        if method.endswith('right'):
            self.x=int(len(img[0])-1)
        if method.startswith('top'):
            self.y=int(1)
        if method.endswith('bottom'):
            self.y=int(len(img)-1)

#Define the pointer that moves over


class pointer:
    def __init__(self, x_, y_, img, print_process=False, Directory='', Target=''):  # Things stored in the pointer:
        self.Target = Target
        self.Directory = Directory
        self.x = x_  # X coordinate
        self.y = y_  # Y coordinate
        self.history = []  # History as list of coordinates
        self.visited = np.zeros(img.shape,dtype=np.uint8) # A 2D-array of cells that are visited by the pointer
        self.visited[self.y, self.x] = 1
        self.print_process = False
        self.imgsum = img.sum()
        self.stepcounter=0
        self.Graph = Create_graph2(img)
        self.r_array = np.zeros(img.shape) + 255  # for black background:  self.r_array = img * 255
        self.g_array = np.zeros(img.shape) + 255  # for black background:  self.r_array = img * 255
        self.b_array = np.zeros(img.shape) + 255  # for black background:  self.r_array = img * 255
        self.CPUtimes = {'moveto': 0, 'move_one_step': 0, 'returnto_fast': 0, 'go_to_next_block': 0, 'finish': 0}
        if print_process:
            os.makedirs(Directory+'/Steps')
            self.print_process = True

    def update(self, x_, y_):  # Update pointer position
        self.history += [[self.x, self.y]]  # Append old position to the history
        self.x = x_  # Change current x
        self.y = y_  # Change current y
        self.visited[self.y, self.x] = 1  # Add current position to visited array
        self.stepcounter += 1
        if (self.stepcounter % 1000) == 0:
            visitsum = self.visited.sum()
            print('Filled {0}/{1}px after {2} steps             '.format(visitsum, self.imgsum, self.stepcounter),end='\r')
        if self.print_process:
            self.r_array[self.y, self.x] = 255
            self.g_array[self.y, self.x] = 0
            self.b_array[self.y, self.x] = 0
            self.r_array[self.history[-1:][0][1], self.history[-1:][0][0]] = 0
            self.b_array[self.history[-1:][0][1], self.history[-1:][0][0]] = 255
            img_outr = Image.fromarray(np.uint8(self.r_array))
            img_outg = Image.fromarray(np.uint8(self.g_array))
            img_outb = Image.fromarray(np.uint8(self.b_array))
            merged = Image.merge("RGB", (img_outr, img_outg, img_outb))
            merged.save('{0}/Steps/step_{1}.png'.format(self.Directory, self.stepcounter))

    def moveto(self,x_,y_): #Move to a coordinate, unrestricted, this will also walk over white cells
        substart=time.time()
        x_dist = x_-self.x
        y_dist = y_-self.y
        for n in range(np.max([abs(x_dist), abs(y_dist)])):
            if not abs(x_dist) == abs(y_dist):
                if abs(x_dist) < abs(y_dist):
                    self.update(self.x, self.y + 1 * get_sign(y_dist))
                    y_dist = y_dist + (-1 * get_sign(y_dist))
                elif abs(x_dist) > abs(y_dist):
                    self.update(self.x + 1 * get_sign(x_dist), self.y)
                    x_dist = x_dist + (-1 * get_sign(x_dist))
            else:
                self.update(self.x + 1 * get_sign(x_dist), self.y + 1 * get_sign(y_dist))
                y_dist = y_dist + (-1 * get_sign(y_dist))
                x_dist = x_dist + (-1 * get_sign(x_dist))
        self.CPUtimes['moveto'] += time.time() - substart
    def move_one_step(self,img): #Move the pointer to the next black cell
        substart=time.time()
        deadend=False
        adjecent_ones = find_adjecent_ones(self.x,self.y,self.history,img)
        if len(adjecent_ones['vh']) == 0:
            targets = adjecent_ones['diag']
        else:
            targets = adjecent_ones['vh']
        if len(targets) >= 1:
            next_cell = targets[0]
        elif len(targets)==0:
            deadend=True
        if not deadend:
            self.CPUtimes['move_one_step'] += time.time() - substart
            self.update(next_cell[0],next_cell[1])
            return True
        else:
            self.CPUtimes['move_one_step'] += time.time() - substart
            return False
    def returnto_fast(self,img):
        substart=time.time()
        Goals = np.transpose(np.array(np.where((img - self.visited) == 1)))
        Goals = [(i[1], i[0]) for i in Goals]
        Path = bfs_shortest_path_goallist(self.Graph,(self.x,self.y),Goals)
        if not Path:
            self.CPUtimes['returnto_fast'] += time.time() - substart
            return False
        else:
            for i in Path:
                self.update(i[0],i[1])
            self.CPUtimes['returnto_fast'] += time.time() - substart
            return True

    def find_returnto_targets(self,img): #Find a cell the pointer can go back to that still has open ends
        cells_to_returnto=[]
        if len(self.returnto) > 0:
            tmp_list=self.returnto.copy()
            for i in tmp_list:
                i_targets=find_adjecent_ones(i[0],i[1],self.history,img)
                if (len(i_targets['diag']) != 0) or (len(i_targets['vh']) != 0):
                    cells_to_returnto+=[i]
                if (len(i_targets['diag']) == 0) and (len(i_targets['vh']) == 0):
                    if i in self.returnto:
                        self.returnto.remove(i)
            if (len(i_targets['diag'])+len(i_targets['vh'])) == 1:
                self.returnto.remove(cells_to_returnto[-1:][0])
        if (len(cells_to_returnto) > 0):
            return cells_to_returnto[-1:][0] #Return the most recently visited one
        else:
            return False
    def go_back_to(self,target,graph):
        movesequence,cost=AStarSearch((self.x,self.y),target,graph)
        for i in movesequence[1:]:
            self.update(i[0],i[1])
    def go_to_next_block(self, img):
        img2=img
        img2[np.where(self.visited==1)]=1
        astar_graph = AStarGraph(img2)
        substart=time.time()
        print('Moving to a different block... Progress:{0}%            '.format(round(((self.visited.sum() / img.sum()) * 100), 2)),end='\r')
        visited_coords = np.array(np.where(self.visited == 1))
        not_visited_coords = np.array(np.where((img - self.visited) == 1))
        chunksize = 10000000
        if (len(visited_coords[0]) * len(not_visited_coords[0]) < chunksize):
            distance_matrix = cdist(np.transpose(visited_coords), np.transpose(not_visited_coords),metric='chebyshev')
            min_distance = distance_matrix.min()
            best_path_index = np.array(np.where(distance_matrix == min_distance))[:, 0]
            goto_visited = visited_coords[:, best_path_index[0]]
            goto_new = not_visited_coords[:, best_path_index[1]]
            goto_visited=[goto_visited[1],goto_visited[0]]
            goto_new=[goto_new[1],goto_new[0]]
        else:
            num_cores = multiprocessing.cpu_count() - 1
            results = Parallel(n_jobs=num_cores)(
                delayed(my_distance)(i, not_visited_coords, visited_coords) for i in range(not_visited_coords.shape[1]))
            overall_min = 1e8
            n1, v1 = [],[]
            for i in results:
                if i[0] == 1: #Sometimes the current version forgets to visit some pxs that it actually could visit
                    v1+=[i[1]] #So save those, and return to them iteratively (using A*)
                    n1+=[i[2]]
                elif i[0] < overall_min:
                    overall_min = i[0]
                    goto_visited = i[1]
                    goto_new = i[2]
            if len(n1) > 0:
                n1=find_best_order(self.x,self.y,n1)
                for i in range(len(n1)):
                    if self.visited[n1[i][1],n1[i][0]] != 1:
                        print('Using A* to move back to {0},{1}...                 '.format(n1[i][0], n1[i][1]),end='\n')
                        self.go_back_to(tuple(n1[i]), astar_graph)
        print('Using A* to move back to {0},{1}...                 '.format(goto_visited[0],goto_visited[1]), end='\n')
        self.go_back_to(tuple(goto_visited),astar_graph)
        print('Moving to a new block at {0},{1}...                             '.format(goto_new[0], goto_new[1]), end='\n')
        self.moveto(goto_new[0],goto_new[1])
        print('Making new graph...{0}                                            '.format(self.visited.sum()),end='\n')
        self.Graph=Create_graph2(img,self.visited)
        self.CPUtimes['go_to_next_block'] += time.time() - substart

    def finish(self,start,img,write_instructions=True): #Wrap up: Return to starting position, and save gif and instructions
        substart=time.time()
        img2 = img
        img2[np.where(self.visited == 1)] = 1
        astar_graph = AStarGraph(img2)
        print('Using A* to move back to starting position {0},{1}            '.format(start.x,start.y),end='\r')
        self.go_back_to((start.x, start.y), astar_graph)
        print('Finishing up... The pointer made {0} steps            '.format(len(self.history)))
        self.history += [[self.x, self.y]]
        self.r_array[np.where(self.visited==1)] = 0
        self.g_array[np.where(self.visited == 1)] = 0
        self.b_array[np.where(self.visited == 1)] = 0
        img_outr = Image.fromarray(np.uint8(self.r_array))
        img_outg = Image.fromarray(np.uint8(self.g_array))
        img_outb = Image.fromarray(np.uint8(self.b_array))
        merged = Image.merge("RGB", (img_outr, img_outg, img_outb))
        merged.save('{0}_finalstep.png'.format(self.Target))
        if write_instructions:
            last_coord = self.history[0]
            with open(self.Target+'.instructions', 'w') as f:
                for i in range(1, len(self.history)):
                    instruction_1 = [self.history[i][n] - last_coord[n] for n in range(2)]
                    f.write('{0},{1}\n'.format(instruction_1[0], instruction_1[1]))
                    last_coord = self.history[i]
        self.CPUtimes['finish'] += time.time() - substart
        print('CPU time per classfunction:')
        for lab,s in self.CPUtimes.items():
            print(lab+':'+' '*(20-(len(lab)))+'{0}'.format(str(datetime.timedelta(seconds=s))))
 






