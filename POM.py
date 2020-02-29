import random as rand
from copy import deepcopy

class PointOfMutation:
    '''
    a data structure for organizing innovations made by NEAT into a cluster-tree
    for data mining the fitness landscape

    PARAMETERS:
        snapshot: a snapshot of the genepool that defines this Point of Mutation
        mascot: the highest scoring member that justifies this Point of Mutation
        radius: the radius that this Point of Mutation covers
    '''
    def __init__(self, snapshot, mascot, parent):
        assert mascot in snapshot, "mascot must be a member of the defining snapshot"

        self.snapshot = snapshot
        self.mascot = mascot
        #set edges for tree structure
        self.parent = parent 
        self.parent.children.append(self)
        
        self.children = []

    def merge(self, otherPOM):
        '''
        merge this Point of Mutation with another due to optimization or increasing radius
        
        PARAMETERS:
            otherPoM: the other PoM to be merged
        '''
        #TODO: going back to best river definition. this can also allow 
        #      for re-evaluation of tree to remove false fitness PoMs
        # TODO: need to deal with edges (tree structure of RoM)

        otherPOM.snapshot = deepcopy(self.snapshot)
        otherPOM.mascot = deepcopy(self.mascot)
        #hackey solution
        if otherPOM.parent is not self.parent:
            otherPOM.parent = self.parent
            otherPOM.children.extend(self.children)
            #TODO: handle children
        else:
            otherPOM.parent = otherPOM.parent.parent
            otherPOM.children.extend(self.children)
        
        #since merging this into other, set other parent and child edges to this
        #copy Nodal_NEAT FSM structure

        #NOTE: this should deiterate all references to this POM as it is not in the otherPoM
    
    def swap(self, population):
        '''
        swap in this Point of Mutation
        
        PARAMETERS:
            population: the size of the genepool that is requesting this PoM
        RETURNS:
            genepool: a list of genomes the size of population generated from snapshots
        '''
        genepool = []
        while len(genepool) < population:
            genepool.append(self.snapshot[rand.randint(0, len(self.snapshot-1))].deepcopy())
        
        return genepool

    