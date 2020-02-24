from organisms.evaluator import evaluator
from POM import PointOfMutation
from page import page
from multiprocessing.managers import BaseManager
import random as rand

#TODO: serve an evaluator from BaseManager on client connect with a lifetime/stagnation
#      value that terminates search when finished and recurses to request another PoM from
#      BaseManager

#TODO: its the burden of ROM to store the tree structure of PoMs. Therefor parent-spawn edges
#      must be maintained and compared here

class RiverOfMutations:
    def __init__(self, radius):
        '''
        orchestrates building a tree of Points of Mutations (PoMs) based on fitness and 
        radius, refered to as a river due to its gradient nature and crossover pressure 
        analogy of genetic algorithms
        PARAMETERS:
            radius: radius of coverage of each PointOfMutation on the fitness landscape
        '''
        #TODO: RoM will be a manager that spawns evaluators (pages) 
        # based on remote processes connecting and serves to clients
        
        self.POMs = [] #POM data structures
        self.pages = [] #POM searchers, analagous to swap space in computer memory architecture

        #initialize root PoM just as evaluator would initialize its genepool. mascot is anything as
        #will immediately optimize with self-merge in first fitness function evaluation
        
        # initPage = 

        initPOM = PointOfMutation()
        POMs = list()
        manager = BaseManager(address = ('', 5000), authkey='bada'.encode())
        manager.register('swap_in', callable = self.swap_in)
        manager.register('merge', callable = self.merge)
        manager.register('update', callable = self.update)

        # self.POMs.append(initPOM)

    def swap_in(self):
        '''
        callable that returns a POM for searching
        '''
        selected = POMs[rand.randint(0, len(POMs)-1)]
        return selected

    def merge(self, PointOfMutation):
        '''
        callable that takes one or more POMs within a radius and returns a single POM describing all of them.
        Pedantic explanation: agglomerative clustering of POMs given similarity (genetic) radius
        '''
        for POM in POMs:
            #also considers optimizations (self merges)
            if PointOfMutation.mascot.fitness > POM and 
                PointOfMutation.mascot.geneticDistance(POM.mascot) <= self.radius:
                PointOfMutation.merge(POM)

    def update(self, PointOfMutation):
        '''
        callable that append a new POM to the POM tree-list
        '''
        #TODO: need to resolve if parent gets merged. should work since merge always merges
        #       into existing POMs but need to verify
        if PointOfMutation.mascot.fitness > parent.mascot.fitness and
            PointOfMutation.mascot.geneticDistance(POM.mascot) > self.radius:
            POMs.append(PointOfMutation)