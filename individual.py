import random,copy
import math

class Func:
    COMPUTE_TYPE = 0# function with this type only can compute
    MODIFY_GRAPH_TYPE = 1#this type function can modify graph
    def __init__(self,f=None,arity=0,type = COMPUTE_TYPE,name = None):
        self.f_ = f
        self.arity = arity
        self.type = type
        self.name = name
    def __call__(self,*argvs,**kwargs):
        return None if not self.f_ else self.f_(*argvs,**kwargs)

class Node:
    def __init__(self):
        self.i_func = None
        self.i_input = []
        self.weight = []
        self.output = None
        self.parameters = []
        self.active = False
    def __eq__(self,other):
        return self.i_func == other.i_func

class Indivadual():
    def __init__(self,func_set,input_len=2,output_len=1,mut_rate=0.03,mut_param = 0.9,gen_len=500):
        self.func_set=func_set
        self.gen=[]
        self.input_len = input_len
        self.output_len = output_len
        self.gen_len = gen_len
        self.mut_rate = mut_rate
        self.mut_param = mut_param
        self.nodes=[]
        self.determined = False
        self.fitness = None
        self.emigration_rate = 0
        self.immigration_rate = 0
        self.active_nodes=set()

        for i in range(self.input_len):
            self.nodes.append(None)
        for i in range(self.gen_len):
            self.nodes.append(self.__create_random_node(i))
        for i in range(1,self.output_len+1):
            self.nodes[-i].active = True
    
    def __create_random_node(self,pos):
        node = Node()
        node.i_func = random.randint(0,len(self.func_set)-1)
        for _ in range(self.func_set[node.i_func].arity):
            node.i_input.append(random.random())
            node.weight.append(random.uniform(-1,1))
        node.i_output = pos
        node.active = False
        return node

    def __determine_active_nodes(self):
        if self.determined:
            return False
        for pos,node in enumerate(reversed(self.nodes)):
            if not node or not node.active:
                continue
            real_pos = len(self.nodes) - 1 - pos
            for val in node.i_input:
                input_index = math.floor(val * real_pos)
                if input_index < self.input_len:
                    continue
                self.nodes[input_index].active = True
        self.determined = True

    def eval(self,*args):
        self.__determine_active_nodes()
        for pos,node in enumerate(self.nodes):
            if not node or not node.active:
                continue
            inputs = []
            for val in node.i_input:
                input_index = math.floor(pos * val)
                if input_index < self.input_len:
                    inputs.append(args[input_index])
                else:
                    inputs.append(self.nodes[input_index].output)
            node.output = self.func_set[node.i_func](*inputs)
        return self.nodes[-1].output

    def mutation(self):
        child = copy.deepcopy(self)
        #child.mut_param = 0.8#random.random()#two type mutation possibillity
        for node in child.nodes:
            if not node:
                continue
            node.active = False
            if random.random() > self.mut_rate:
                continue
            if random.random() < child.mut_param:#signle point mutation
                node.i_func = random.randint(0,len(self.func_set)-1)
                for i in range(len(node.i_input)):
                    if random.random() < self.mut_rate:
                        node.i_input[i] = random.random()
            else:#opposite position mutation
                mid_func_pos = len(self.func_set) // 2
                opposite_pos = len(self.func_set) - 1 - node.i_func
                (start,end) = (mid_func_pos,opposite_pos) if mid_func_pos < opposite_pos else (opposite_pos,mid_func_pos)
                node.i_func = random.randint(start,end)
                for i in range(len(node.i_input)):
                    if random.random() < self.mut_rate:
                        mid_pos = 0.5
                        opposite_pos = 1 - node.i_input[i]
                        (start,end) = (mid_pos,opposite_pos) if mid_pos < opposite_pos else (opposite_pos,mid_pos)
                        node.i_input[i] = random.uniform(start,end)
        for i in range(1,self.output_len+1):
            child.nodes[-i].active = True
        child.determined = False
        return child
    def mutation_2(self):
        child = copy.deepcopy(self)
        for node in child.nodes:
            if not node:
                continue
            node.active = False
        for i in range(1,self.output_len+1):
            child.nodes[-i].active = True
            for j in range(len(child.nodes[-i].i_input)):
                child.nodes[-i].i_input[j] = random.random()
        child.determined = False
        return child
    def reset_nodes(self):
        for node in self.nodes:
            if not node:
                continue
            node.active = False
        for i in range(1,self.output_len+1):
            self.nodes[-i].active = True
        self.determined = False
    def opposite_individual(self):
        opposite_ind = copy.deepcopy(self)
        for node in opposite_ind.nodes:
            if not node:
                continue
            node.active = False
            mid_func_pos = len(self.func_set) // 2
            opposite_pos = len(self.func_set) - 1 - node.i_func
            (start,end) = (mid_func_pos,opposite_pos) if mid_func_pos < opposite_pos else (opposite_pos,mid_func_pos)
            node.i_func = random.randint(start,end)
            for i in range(len(node.i_input)):
                mid_pos = 0.5
                opposite_pos = 1 - node.i_input[i]
                (start,end) = (mid_pos,opposite_pos) if mid_pos < opposite_pos else (opposite_pos,mid_pos)
                node.i_input[i] = random.uniform(start,end)
        for i in range(1,self.output_len+1):
            opposite_ind.nodes[-i].active = True
        opposite_ind.determined = False
        return opposite_ind
    def opposite_ind(self):
        if not self.determined:
            self.__determine_active_nodes()
        opposite_ind = copy.deepcopy(self)
        active_node_index = []
        for pos,node in enumerate(opposite_ind.nodes):
            if not node:
                active_node_index.append(pos)
                continue
            if not node.active:
                active_node_index.append(pos)
                node.active = True
                continue
            node.active = False
        for i in range(1,self.output_len+1):
            opposite_ind.nodes[-i].active = True
        opposite_ind.determined = False
        
        active_node_index.append(len(opposite_ind.nodes) - 1)
        
        for pos,node in enumerate(reversed(opposite_ind.nodes)):
            if not node:
                continue
            if node.active:
                index = active_node_index.index(len(opposite_ind.nodes) - 1 - pos)
                for i in range(len(node.i_input)):
                    if i == 0:
                        input_pos = active_node_index[index - 1 if index - 1 >=0 else 0]
                    else:
                        input_pos = active_node_index[random.randint(0,index - 1)]
                    node.i_input[i] = random.uniform(input_pos/(len(opposite_ind.nodes) - 1 - pos),\
                    (input_pos+1)/(len(opposite_ind.nodes) - 1 - pos))
        return opposite_ind