from individual import Indivadual,Func
import math,random,copy
import time
import operator as op     
import matplotlib.pyplot as plt

def generate_data(func,data_num = 21):
    data = []
    for i in range(1,data_num):
        data.append((i,func(i)))
    return data

def protect_div(a,b):
    if abs(b) < 1e-10:
        return a
    return a/b   
funcation_table = [Func(op.add,2),Func(op.mul,2),Func(op.sub,2),Func(protect_div,2)]

class CGP_test():
    def __init__(self,test_func,children_size=50,mut_rate=0.3,gen_len = 20,opposite_rate = 0.9):
        self.children_size = children_size
        self.mut_rate = mut_rate
        self.opposite_rate = opposite_rate
        self.gen_len = gen_len
        self.population = []
        self.population_parent = None
        self.second_parent = None
        self.train_data = generate_data(test_func,data_num=21)
        self.freezed_iterators = 0
        self.change_parent_parameter = 20
        self.__init_pop()
    def __init_pop(self):
        for _ in  range(self.children_size+1):
            self.population.append(Indivadual(input_len=1,output_len=1,func_set=funcation_table,
            mut_rate=self.mut_rate,gen_len=self.gen_len,mut_param=0.9))
        self.evaluate_individul(self.population)
        self.population.sort(key = lambda ind: ind.fitness)
        self.population_parent = self.population[0]
    def evaluate_individul(self,population):
        train_data = self.train_data
        BIG_ERROR_NUM = 10e10
        for ind in population:
            hit_score = 0
            error_sum = 0
            for data in train_data:
                try:
                    error = abs(ind.eval(data[0])-data[1])
                except OverflowError:
                    error_sum += BIG_ERROR_NUM
                    print('overflow')
                else:
                    if error < 0.01:
                        hit_score += 1
                    error_sum += error
            ind.fitness = error_sum
            ind.hit = hit_score
    def calculate_migration_rate(self):
        pass
    def evolve(self):
        parent = self.population_parent
        if self.freezed_iterators == self.change_parent_parameter:
            self.freezed_iterators = 0
            parent = self.population_parent.opposite_ind()
        children = []
        for _ in range(self.children_size):
            child = parent.mutation()
            if random.random() < self.opposite_rate:
                children.append(child.mutation_2())
            children.append(child)
        self.evaluate_individul(children)
        children.sort(key = lambda ind: ind.fitness)
        if self.population_parent.fitness > children[0].fitness:
            self.population_parent = children[0]
            self.freezed_iterators = 0
        elif abs(self.population_parent.fitness - children[0].fitness) < 1e-10:
            self.population_parent = children[0]
            self.freezed_iterators += 1
        else:
            self.freezed_iterators += 1
        if self.freezed_iterators == self.change_parent_parameter:
            self.second_parent = copy.deepcopy(children[random.randint(0,len(children) - 1)])
    def run(self,generations = 10000):
        index = 1
        error_squence = []
        forever = True  if generations == -1 else False
        while index < generations or forever:
            self.evolve()
            error_squence.append((index,self.population_parent.fitness))
            if self.population_parent.hit == len(self.train_data):
                break
            index += 1
        return (error_squence,{'generation':index,'hit':self.population_parent.hit,'error':self.population_parent.fitness})
funcs = [
    #lambda x:x*x
    lambda x: math.pow(x,6) - 2*math.pow(x,4) + math.pow(x,2),
    #lambda x: (math.pow(x,3) + x)/2,
    #lambda x: (math.pow(x,2) + x + 2)/2
]
opposite_rates = [0.8,0.9,1.0]
filenames = [
    'record/record_x6_random_change_p.txt',
    'record/magic_number_random_change_p.txt',
    'record/lazy_squence_random_change_p.txt',
    #'record/test.txt'
    ]
for pos,func in enumerate(funcs):
    result = []
    for i in range(100):
        cgp = CGP_test(func,children_size=20,gen_len=20,mut_rate=0.3)
        result.append(cgp.run(10000)[0])
    for index,obj in enumerate(result):
        x = []
        y = []
        for item in obj:
            x.append(item[0])
            y.append(item[1])
        plt.plot(x,y,'*-')
    plt.show()
