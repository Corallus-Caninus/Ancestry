import random as rand
from copy import deepcopy

class PointOfMutation:
    def __init__(self, snapshot, mascot, parent):
        '''
        a data structure for organizing innovations made by NEAT into a cluster-tree
        for data mining the fitness landscape
        PARAMETERS:
            snapshot: a snapshot of the genepool that defines this Point of Mutation
            mascot: the highest scoring member that justifies this Point of Mutation
            radius: the radius that this Point of Mutation covers
        '''
        assert mascot in snapshot, "mascot must be a member of the defining snapshot"

        self.snapshot = snapshot
        self.mascot = mascot
        # self.parent = parent #TODO: this creates root node boostrapping shenanigans
    
    def merge(self, otherPOM):
        '''
        merge this Point of Mutation with another due to optimization or increasing radius
        PARAMETERS:
            otherPoM: the other PoM to be merged
        '''
        # TODO: do merges extend, (increasingly large snapshot) or consider only genomes within fitness radius?
        #       extension is intuitive for representing latent vector in fitness landscape but may get too large.
        # self.snapshot.extend(otherPoM.snapshot)
        otherPOM.snapshot.extend(self.snapshot)
        # TODO: increase mascot count or take fittest?
        # if self.mascot.fitness < otherPoM.mascot.fitness:
        #     self.mascot = otherPoM.mascot
        if otherPoM.mascot.fitness < self.mascot.fitness:
            otherPoM.mascot = self.mascot
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

    def location(self):
        '''
        get the genetic location of this Point of Mutation
        RETURNS:
            innovations: a list of innovations that define this PoMs mascot
        '''
        return [x.innovation for x in self.mascot.getAllConnections()]