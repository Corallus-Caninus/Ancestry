from organisms.evaluator import evaluator
from organisms.innovation import globalInnovations
from organisms.nuclei import nuclei
from POM import PointOfMutation
from page import page
import random as rand

# TODO: the ROM is the shared object seen by manager. extract manager/server to server.py and
#       page implementing program to client.py This can allow for yaml kubernetes and general
#       resource negotiator targeting in the future.
#
# NOTE: going with River model where number on parent edges and child edges at a PoM is 'river width' and 
#       considering merges across domains/ranges is proportional to generalization score and 
#       'innovation richness'. Which should be biased for selection on load() calls

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
    #NOTE: this is also known as Ancestral Speciation but Rivers of Mutations 
    #      is a little more descriptive.
    #NOTE: node depth in river is proportional to fitness AND complexity due to 
    #      justified complexification when considering new Points of Mutations.

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
        self.POMs = list()

        #stores all discovered innovations from all page searchers
        self.innovation_map = globalInnovations()

        
    #TODO: need to send a partial with globalInnovations kept here
    def load(self):
        '''
        callable that returns a POM for searching with the currently discovered innovations.
        '''
        if len(self.POMs) < 1:
            return False #signal that the page needs to search initial POM
        selected = self.POMs[rand.randint(0, len(self.POMs)-1)]

        return selected
    
    def load_map(self):
        '''
        getter for innovation_map used in page
        '''
        return self.innovation_map

    #TODO: need to check incoming globalInnovations in below methods
    #      iterate through genepool and verifyConnection. verifyNode on split depths

    def update(self, PointOfMutation):
        #NOTE: Pedantic explanation: agglomerative clustering of POMs given similarity (genetic) radius
        '''
        attempt to add or merge this POM to the ROM and update globalInnovations if still relevant
        
        PARAMETER:
            PointOfMutation: a PointOfMutation object to be considered for integrating into the RoM
        '''
        noveltyComparator = lambda x,y: x.geneticDistance(y, 
            self.excessMetric, self.disjointMetric, self.connectionMetric) > self.radius       
        
        if PointOfMutation.mascot.fitness > PointOfMutation.parent.mascot.fitness and \
            all([noveltyComparator(x, PointOfMutation.mascot) for x in self.POMs]):
            #accept the new POM
            self.POMs.append(PointOfMutation)
        else:
            mergeComparator = lambda POM: PointOfMutation.mascot.fitness > POM and \
                                PointOfMutation.mascot.geneticDistance(POM.mascot, \
                                self.disjointMetric, self.excessMetric, self.connectionMetric) <= self.radius
            blob = filter(mergeComparator, self.POMs)
            map(PointOfMutation.merge, blob)

            #reset the fitness gradient
            #@DEPRECATED
            # self.POMs = filter(lambda x: x.parent.mascot.fitness < x.mascot.fitness, self.POMs)
            
            #form a 'blob' that defines all POMs getting removed from merge operation            
            parentBlobClosures = filter(lambda x: x.parent in blob, blob)
            childBlobClosures = filter(lambda x: any([y in x.children for y in blob]), blob)
            # now seam all gaps caused by removing closures
            for parentSeam in parentBlobClosures:
                #climb upstream until out of blob or root node
                while parentSeam.parent is not None and parentSeam.parent in blob:
                    parentSeam.parent = parentSeam.parent.parent
            for childSeam in childBlobClosures:
                childSeam.children = [x for x in childSeam.children if x not in blob]

            

    def update_map(self, incomingGenepool):
        #TODO: call on POM tree-list update
        #NOTE: splitDepth data structure template:
        # genome[split] =
        #   [node1, node2, ..]
        #   list index = splitDepth
        tmpNuclei = nuclei()
        for g in incomingGenepool:
            tmpNuclei.readyPrimalGenes(g)
            for split in tmpNuclei.primalGenes[g]:
                #verify nodes then connections
                # TODO: look back a split depth for resultant connection
                for con in split:
                    for outNode in con.outputNode:
                        self.innovation_map.verifynode()
                        pass
                    for inNode in con.inputNode:
                        pass

        #iterate through all splits and verify connections and nodes
