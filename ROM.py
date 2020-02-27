from organisms.evaluator import evaluator
from organisms.innovation import globalInnovations
from POM import PointOfMutation
from page import page
import random as rand

#TODO: the ROM is the shared object seen by manager. extract manager/server to server.py and
#      page implementing program to client.py This can allow for yaml kubernetes and general
#       resource negotiator targeting in the future.
#
#TODO: its the burden of ROM to store the tree structure of PoMs. Therefor parent-spawn edges
#      must be maintained and compared here

class RiverOfMutations:
    '''
    orchestrates building a river (gradient tree) of Points of Mutations (PoMs) based on fitness and 
    radius. Refered to as a river due to node depth being proportional to fitness
    and crossover pressure analogy of genetic algorithms.
    
    PARAMETERS:
        radius: radius of coverage of each PointOfMutation on the fitness landscape
    CONSTRUCTS:
        a BaseManager that serves with methods for updating the river data structure from pages (POM searchers)
    '''
    #NOTE: node depth in river is proportional to fitness and complexity due to 
    #      justified complexification operation

    def __init__(self, radius, excessMetric, disjointMetric, connectionMetric):
        #TODO: need to track global innovations here.
        #      can either update every generation from all pages (costly bottleneck)
        #      or can implement a globalInnovations.join(globalInnovations). 
        #      this method would also allow crossover in parallel.
        self.radius = radius
        self.excessMetric = excessMetric
        self.disjointMetric = disjointMetric
        self.connectionMetric = connectionMetric


        self.POMs = [] #POM data structures

        #TODO: dont initialize, let evaluator from page return the first. if no POM in manager
        #      create initial evaluator in page
        # initPOM = PointOfMutation()
        self.POMs = list()
        # self.POMs.append(initPOM)
        #TODO: implement globalInnovations and call 
        #      self.innovations.join(page.innovations) on manager merge
        self.innovations = globalInnovations()

        
    #TODO: need to send a partial with globalInnovations kept here
    def load(self):
        '''
        callable that returns a POM for searching with the currently discovered innovations.
        '''
        if len(self.POMs) < 1:
            return False #signal that the page needs to search initial POM
        selected = self.POMs[rand.randint(0, len(self.POMs)-1)]
        # selected = selected.swap(population)
        # return selected, self.innovations
        return selected
    
    def registerInnovations(self):
        return self.innovations

    #TODO: need to check incoming globalInnovations in below methods
    #      iterate through genepool and verifyConnection. verifyNode on split depths

    def update(self, PointOfMutation):
        #NOTE: Pedantic explanation: agglomerative clustering of POMs given similarity (genetic) radius
        '''
        attempt to add or merge this POM to the ROM and update globalInnovations if still relevant.
        '''
        noveltyComparator = lambda x,y: x.geneticDistance(y, 
            self.excessMetric, self.disjointMetric, self.connectionMetric) > self.radius       
        
        if PointOfMutation.mascot.fitness > PointOfMutation.parent.mascot.fitness and \
            all([noveltyComparator(x, PointOfMutation.mascot) for x in self.POMs]):
            
            #@DEPRECATED
            # PointOfMutation.mascot.geneticDistance(POM.mascot, 
            #     self.disjointMetric,self.excessMetric, self.connectionMetric) > self.radius:
            
            #accept the new POM
            self.POMs.append(PointOfMutation)
        else:
            for POM in self.POMs:
                #also considers optimizations (self merges)
                #
                # TODO: how does merge to parent effect this. when a POM is optimized how
                #       does the fitness gradient be forced, safe currently since merge 
                #       still has to pass condition here. cleanup POM ordering here.

                if PointOfMutation.mascot.fitness > POM and \
                    PointOfMutation.mascot.geneticDistance(POM.mascot, \
                        self.disjointMetric, self.excessMetric, self.connectionMetric) <= self.radius:
                    #accept the merged POM solution
                    PointOfMutation.merge(POM)
            
            #reset the fitness gradient
            self.POMs = filter(lambda x: x.parent.mascot.fitness < x.mascot.fitness, self.POMs)
            # TODO: reset parents (edges)

    def inheritInnovations(self, localInnovations):
        #TODO: verifyConnection and verifyNode using connections and primalGenes from
        #       incoming PointOfMutation snapshot
        # always call on merge or update
        
        pass