from organisms.evaluator import evaluator
from multiprocessing.managers import BaseManager


class page:
    def __init__(self, timeout, channel, parentPOM):
        '''
        an PointOfMutation processor with a timeout/stagnation condition (lifetime) for searching a
        Point of Mutation. Also contains routines for communicating updates and requesting
        a new Point of Mutation from a River of Mutation manager instance upon timeout.

        PARAMETERS:
            timeout: time allotted to search this Point of Mutation
            channel: list of strings [address,port] of RoM manager server instance to communicate page swaps and updates
            
            @DEPRECATED: evaluator initialization extracted to RoM
            fitnessFunction: function to be optimized (should be same across all pages for now)
            fitnessObjective: fitness score threshold where function has been solved

            parentPOM: POM that spawned this page 
            similarity: distance that defines a POM. for optimization a superior solution
                        must be within this distance. 
        '''
        self.timeout = timeout
        self.channel = channel
        # self.fitnessFunction = fitnessFunction
        # self.fitnessObjective = fitnessObjective

        #setup river pipeline
        self.pipeline = BaseManager(address=(self.channel[0], self.channel[1]),authkey='bada'.encode())
        try:
            self.pipeline.connect()
        except:
            raise Exception("Could not connect to river pipeline..")
        #register the feeder method from RoM
        # self.pipeline.register('swap_in', callable=lambda: swap_in)
        self.pipeline.register('swap_in')
        #register the POM discovery method
        # self.pipeline.register('update', callable=lambda: update)
        self.pipeline.register('update')
        #register the merge operation
        # self.pipeline.register('merge', callable = lambda: merge)
        self.pipeline.register('merge')

        self.searcher = self.pipeline.swap_in()

    def exec():
        #TODO: NOTE that these methods are not garunteed time of arrival and must check if
        #      operations are still viable e.g.: if a merge still breaks a PoMs high score
        #      by the time its processed
         
        for _ in timeout:
            self.searcher.nextGeneration(fitnessFunction, fitnessObjective)

            #TODO: need to return a new PointOfMutation on merge and update conditions 
            #             
            #POM discovery condition
            # if any([x.fitness >  for x in super.genepool])
            #
            #POM optimization condition
            #TODO: should have getHighScore in evaluator once fitness is fixed
            # elif parentPOM.mascot.fitness < max([x.fitness for x in self.searcher.genepool])
            #       and parentPOM.mascot.geneticDistance(max([x.fitness for x in self.searcher.genepool])
            #           < )
            #
            # fitness objective reached condition
            # elif
            #return None

        self.searcher = self.pipeline.swap_in()
        return self.exec()