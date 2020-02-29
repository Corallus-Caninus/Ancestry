from organisms.evaluator import evaluator
from organisms.innovation import globalInnovations as localInnovations
from multiprocessing.managers import BaseManager
from POM import PointOfMutation
import random as rand

class page:
    '''
    a PointOfMutation processor with a timeout/stagnation condition (lifetime) for searching a
    Point of Mutation. Also contains routines for communicating updates and requesting
    a new Point of Mutation from a River of Mutation manager instance upon timeout.

    PARAMETERS:
        timeout: time allotted to search this Point of Mutation
        channel: list of strings [address,port] of RoM manager server instance to communicate page swaps and updates
        
        fitnessFunction: function to be optimized (should be same across all pages for now)
        fitnessObjective: fitness score threshold where function has been solved

        parentPOM: POM that spawned this page 
        similarity: distance that defines a POM. for optimization a superior solution
                    must be within this distance. 
    '''
    #NOTE: referred to as a 'page' due to the analogy of swap space and main memory in 
    #      computer architecture, allowing ancestral speciation (ROM) to cover a search 
    #      space larger than normally possible by swapping in and out Points of Mutation.

    def __init__(self, timeout, channel, parentPOM, fitnessFunction, fitnessObjective):
        self.timeout = timeout
        self.channel = channel
        self.fitnessFunction = fitnessFunction
        self.fitnessObjective = fitnessObjective
        self.localInnovations = localInnovations

        #setup river pipeline
        class pageManager(BaseManager): pass
        pageManager.register('link')
        self.pipeline = pageManager(address=(self.channel[0], self.channel[1]),authkey='bada'.encode())
        try:
            self.pipeline.connect()
            self.river = self.pipeline.link() #link a shared river object to this page
        except:
            raise Exception("Could not connect pipeline to river..")

        self.load_page()

    def load_page(self):
        '''
        load a PointOfMutation into this executor for search from a river shared pipeline object.
        '''
        self.eval = evaluator(inputs=2, outputs=1, population=100,
                    connectionMutationRate=0.5,nodeMutationRate=0.01,weightMutationRate=0.6,
                    weightPerturbRate=0.9,selectionPressure=3)

        self.loadedPOM = self.river.load()
        # if river in uninitialized, start searching from init topology.
        if self.loadedPOM is not None: 
            self.eval.genepool = self.loadedPOM.swap(len(self.eval.genepool))
            #load in innovations from river to hopefully speed up verification and prevent memory bloat
            self.eval.globalInnnovations = self.river.load_map()
        
        #@DEPRECATED
        # self.eval.genepool, self.eval.globalInnovations = self.pipeline.swap_in(len(self.eval.genepool))
        
    def exec(self):
        '''
        search for timeout generations, updating the river when the condition is met and retrieving
        a new PointOfMutation when timeout is reached unless a new POM is discovered.
        '''
        #TODO: NOTE that these methods are not guaranteed time of arrival and must check if
        #      operations are still viable e.g.: if a merge still breaks a PoMs high score
        #      by the time its processed
        for _ in self.timeout:
            self.eval.nextGeneration(self.fitnessFunction, self.fitnessObjective)
            if any([x.fitness > self.fitnessObjective for x in self.eval.genepool]):
                potential = PointOfMutation(self.eval.genepool, max([x for x in self.eval.genepool], \
                    key=lambda x: x.fitness), self.loadedPOM.parent)

                #check if it is justified complexification or a merge
                self.river.update(potential)
                #continue search with new POM loaded
                return self.exec()        

        self.load_page()
        return self.exec()
