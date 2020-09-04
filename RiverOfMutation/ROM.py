import random as rand
from itertools import chain
import pickle

from organisms.Nuclei import Nuclei
from organisms.innovation import GlobalInnovations


# NOTE: going with River model where PoM vertex degree ('river width') and
#       merges across domains/ranges is proportional to generalization 
#       score and 'innovation richness'. Which should be biased for selection 
#       on load() calls
#
# TODO: add re-evaluation on swap in for non-deterministic fit. landscape POMDP's
#       do this later.
#
# TODO: add s3 serialize and save method on update. (overwrite previous)

class RiverOfMutations:
    # NOTE: this is Ancestral Speciation but Rivers of Mutations
    #      is a little more descriptive to the natural gradient thing.
    def __init__(self, radius, excess_metric, disjoint_metric, connection_metric):
        """
        orchestrates building a river (gradient tree) of Points of Mutations (PoMs) based
        on fitness and radius. Referred to as a river due to Node depth being proportional
        to fitness and crossover pressure analogy of genetic algorithms.

        PARAMETERS:
            radius: radius of coverage of each PointOfMutation on the fitness landscape
        CONSTRUCTS:
            a BaseManager that serves with methods for updating the river data structure
            from pages (POM searchers)
        """
        # TODO:  need to track global innovations here.
        #       can either update every generation from all pages 
        #       (costly bottleneck)
        #       or can implement a GlobalInnovations.join(GlobalInnovations).
        #       this method would also allow crossover in parallel.
        self.radius = radius
        self.excessMetric = excess_metric
        self.disjointMetric = disjoint_metric
        self.connectionMetric = connection_metric

        self.POMs = []  # POM data structures

        # stores all discovered innovations from all Searcher searchers
        # TODO: how does this behave with shared object.
        self.global_primals = Nuclei()
        self.global_innovation_map = GlobalInnovations()

    # TODO: implement a selection policy. need to walk POMs as tree 
    #       not index as list self.POMs
    def load(self):
        """
        callable that returns a POM for searching with the currently discovered
        innovations.
        """
        print('Request: load PoM..')
        selection = rand.randint(0, len(self.POMs))
        if selection == len(self.POMs):
            # TODO:  how is rooted tree structure represented? some form
            #       of dummy root Node should be used to implicate init
            #       topology. This will become important in graphics and
            #       other forms of explainability. all my ML projects
            #       need to have a file format associated with
            #       high level objects. (e.g.: Nodal_NEAT Genome representation)
            #       if only for cross language implementations and information
            #       extraction.
            # tell the client to search the initPOM (initial topology)
            print('Request: sent init PoM ')
            return None
        else:
            print('Request: sent PoM {}'.format(self.POMs[selection]))
            # TODO: send global innovations. this should be only place this
            #       is necessary since only place evaluator is bootstrapped
            return self.POMs[selection]

    def load_map(self):
        """
        getter for global_innovation_map used in Searcher
        """
        print('Request: innovation map')
        return self.global_innovation_map

    # TODO: need to serialize and store to object storage solution (S3)
    #       on each update (should async if possible this is a server after all)
    #       use fitness function serialized bytestream checksum as folder name
    #       serialize and save entire ROM.
    # TODO: copy destroys tree, this is exemplified on swapin of PoM where nodes lose connections
    #       this is inconsistent and is an edge case (bug somewhere sparse) seems to happen during
    #       initialization.
    def update(self, PointOfMutation):
        """
        attempt to add or merge this POM to the ROM and update GlobalInnovations
        if still relevant

        PARAMETER:
            PointOfMutation: a PointOfMutation object to be considered for
                             integrating into the RoM
        """
        print('Received: POM update attempt..')
        print('Current RoM..')
        for p in self.POMs:
            print(p)
        print('end of RoM.')

        def mergeComparator(POM):
            # return PointOfMutation.mascot.fitness > POM and PointOfMutation.mascot.geneticDistance(
            return PointOfMutation.mascot.fitness > POM.mascot.fitness and PointOfMutation.mascot.geneticDistance(
                POM.mascot, self.disjointMetric, self.excessMetric, self.connectionMetric) < self.radius

        def noveltyComparator(x, y):
            return x.mascot.geneticDistance(y.mascot, self.excessMetric, self.disjointMetric,
                                            self.connectionMetric) > self.radius

        # translate genepool to local coordinate system
        self.update_map(PointOfMutation.snapshot)

        # TODO: this is a little strange, would prefer initializing self.POMs on RoM.__init__()
        #       might rework anchored initPOM into RoM at some point.
        # NOTE:  currently using the initPOM score is 0, any diversity qualifies
        #       initPOM representation.
        if len(self.POMs) == 0:
            self.POMs.append(PointOfMutation)
            print('returning from RoM PoM initialization')
            return
        print('update existing RoM..')

        # TODO: ensure or doesnt check second condition after first fails
        if PointOfMutation.parent is None or PointOfMutation.mascot.fitness > PointOfMutation.parent.mascot.fitness:
            # new POM
            print('Adding PoM to RoM.. {}'.format(PointOfMutation))
            if all([noveltyComparator(x, PointOfMutation) for x in self.POMs]):
                # accept the new PoM
                self.POMs.append(PointOfMutation)
            # merge/optimize PoM
            else:
                blob = filter(mergeComparator, self.POMs)
                map(PointOfMutation.merge, blob)
                self.POMs.append(PointOfMutation)
                for pom in [x for x in blob if x is not PointOfMutation]:
                    print('Removing PoM from RoM.. {}'.format(pom))
                    self.POMs.remove(pom)

            with open('RoM.pkl', 'wb') as w:
                pickle.dump(self, w)

    # NOTE: this must be called before distance comparison/merge update since this translates geneitc position
    # need to search top down for each respective verification
    # TODO: this should be a PointOfMutation not genepool
    # TODO: might be missing innovation here or locally. need more test (graphics would likely solve lots of problems.)
    def update_map(self, incomingGenepool):
        '''
        processes the incoming genepool with known innovations to keep globalInnovations consistent.
        '''
        # TODO: currently have to process all snapshots. Should rewrite this to store node references
        #       or something. this is entirely too expensive and requires a server with lots of compute
        # TODO: probably have to write a new method since nodeId iteration is the fundamental synchronization
        #       mechanism for connection innovation.

        # TODO: if this is kept, make local variable and update at the end of this method.
        allNodes = list(chain(*[[y.hiddenNodes for y in x.snapshot] for x in self.POMs]))
        # print('got all nodes: {}'.format(allNodes))
        for g in incomingGenepool:
            # prepare temporary primalGenes for incoming topology
            if g not in self.global_primals.primalGenes:
                self.global_primals.readyPrimalGenes(g)
            # Thm: if this is performed from top down (init topology to split depths of full primal topology),
            #       should set nodeId's correctly.
            depth = 0
            # TODO: use splitConnections from global_innovation instead
            #       since init topology is always the same, get splits for
            #       nodes at given depths
            for incoming in self.global_primals.primalGenes[g]:
                depth += 1
                for n in incoming:
                    # print('verifying node: {} \n at depth: {} \n'.format(n, depth))

                    c = None
                    for c in g.getAllConnections():
                        if n.alignNodeGene(c):
                            split_trace = c
                            break
                    assert c is not None, 'split connection not in incoming genome!'

                    # TODO: ensure this references node in genepool.
                    # since shallow copied from depth buffer in readyPrimalGenes this should hold reference..
                    # will create a strange and posterior error if not..
                    # TODO: this is gross. refactor this method to return nodeId if this is what it will do.
                    n.nodeId = self.global_innovation_map.verifyNode(allNodes, c).nodeId

                for n in incoming:
                    for c in n.outConnections + n.inConnections:
                        # print('updating connection {} at depth {}'.format(c, depth))
                        self.global_innovation_map.verifyConnection(c)

            # reset incoming primalGenes
            self.global_primals.primalGenes[g].clear()
