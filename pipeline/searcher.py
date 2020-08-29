from copy import deepcopy
from multiprocessing.managers import BaseManager

from RiverOfMutation.POM import PointOfMutation
from organisms.Evaluator import Evaluator
from organisms.innovation import GlobalInnovations as localInnovations


# NOTE:  this allows implementation of hyperparameter sweep via searchers.
#        Eventually automate this so the environment alters mutation rates.
#        would also like remove distance parameter for PoM radius.
#
#       need to resolve:
#       RoM structure since edges are no longer finite sample space.
#           |_large mutation rates encroach on higher complexities even with
#           |_fixed timeout. Maybe an edge attribute? this would make degree of
#           |_generalization more complex.
# NOTE: can always use lower level shared Queue if this starts failing or needs
#       simple optimization.
# TODO: rename to searcher or something Searcher is a little too forced of a metaphore
class Searcher:
    def __init__(self, timeout, address, fitnessFunction, fitnessObjective):
        """
         a PointOfMutation processor with a timeout/stagnation condition (lifetime) for searching a
         Point of Mutation. Also contains routines for communicating updates and requesting
         a new Point of Mutation from a River of Mutation manager instance upon timeout.

         PARAMETERS:
             timeout: time allotted to search this Point of Mutation
             address: list of strings [address,port] of RoM manager server instance to
                      communicate Searcher swaps and updates

             fitnessFunction: function to be optimized (should be same across all pages for now)
             fitnessObjective: fitness score threshold where function has been solved
         """

        self.timeout = timeout
        self.address = address
        self.fitnessFunction = fitnessFunction
        self.fitnessObjective = fitnessObjective
        self.localInnovations = localInnovations
        self.loadedPOM = None

        # setup river pipeline
        class PageManager(BaseManager):
            pass

        PageManager.register('River')
        # NOTE: it is standard practice for a given application to statically
        #       allocate a port. forwarding allows enough customization
        self.pipeline = PageManager(address=(self.address,
                                             5000), authkey='bada'.encode())
        # self.address[1]),authkey='bada'.encode())
        try:
            # TODO: add some ncurses server stdout backend stuff
            print('connecting..')
            self.pipeline.connect()
            print('connected.\n acquiring RoM shared object..')
            # link a shared river object to this Searcher
            self.river = self.pipeline.River()
            print('RoM acquired.')
            print('RoM object: ', dir(self.river))
        except:
            raise Exception("Could not connect this pipeline to River..")

        self.evaluator = Evaluator(inputs=2, outputs=1, population=100,
                                   connectionMutationRate=0.5, nodeMutationRate=0.01,
                                   weightMutationRate=0.6, weightPerturbRate=0.9,
                                   selectionPressure=3)

        # preserved here for reference. probably a more space efficient way
        # but #Python
        # TODO: hold POM objects here for merging since this now
        #       handles all POM initialization and qualifying comparison
        self.initGenepool = deepcopy(self.evaluator.genepool)
        self.load()

    def create_POM(self):
        """
        create a POM with the current genepool.
        """
        # TODO: first condition may be failing
        if self.loadedPOM is not None:
            potential = PointOfMutation(self.evaluator.genepool, max([x for x in self.evaluator.genepool],
                                                                     key=lambda x: x.fitness), self.loadedPOM)
        else:
            potential = PointOfMutation(self.evaluator.genepool, max([x for x in self.evaluator.genepool],
                                                                     key=lambda x: x.fitness), None)

        return potential

    def load(self):
        """
        load a PointOfMutation into this executor for search from a river shared-object
        pipeline.
        """
        # NOTE: shouldn't have to reload Evaluator each call just swap out population
        #       and update globalInnovation

        self.loadedPOM = self.river.load()
        print('received {} PoM..'.format(self.loadedPOM))
        # if river in uninitialized, start searching from init topology.
        if self.loadedPOM is not None:
            self.evaluator.genepool = self.loadedPOM.swap(len(self.evaluator.genepool))
            # load in innovations from river to hopefully speed up verification \
            # and prevent memory bloat
        else:
            print('received initial PoM..')
            self.evaluator.genepool = deepcopy(self.initGenepool)
            self.loadedPOM = self.create_POM()

        self.evaluator.globalInnnovations = self.river.load_map()

    def refresh(self, potential):
        """
        continue searching the current PoM but retrieve updated
        innovations and update the river
        """
        print('refreshing searcher..')
        fresh = self.create_POM()
        self.river.update(fresh)
        self.loadedPOM = fresh
        self.evaluator.globalInnovations = self.river.load_map()
        return self.exec()

    # TODO: load in merged solution on RoM merge (this all needs to be traced
    #       against RoM tree operations and structure
    def exec(self):
        """
        search for timeout generations, updating the river when the condition is met and
        retrieving a new PointOfMutation when timeout is reached unless a new POM
        is discovered.
        """
        for time in range(0, self.timeout):
            print('searching.. {}'.format(time))
            self.evaluator.nextGeneration(self.fitnessFunction)

            # TODO: dont call create_POM every time.
            #potential = self.create_POM()

            # merge PoM condition
            # check if locally justified complexification
            # TODO: refactor these conditions
            if any([x.fitness > self.loadedPOM.mascot.fitness for x in self.evaluator.genepool]):
                # TODO: should wait for update to see if this searcher is far behind others and should
                #       load instead of recurse. not critical if this is a very inferior solution
                #       the likelihood of timeout in the next evaluation is higher
                return self.refresh()

            # terminal condition
            if any([x.fitness > self.fitnessObjective
                    for x in self.evaluator.genepool]):
                # keep searching since alternate conventions still exist
                print('search complete.')
                return self.refresh()

        # timeout has occured, request a new PoM to search
        print('search timeout, restarting..')
        self.load()
        return self.exec()
