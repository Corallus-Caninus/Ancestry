import random as rand

from organisms.Nuclei import Nuclei
from organisms.innovation import GlobalInnovations


# NOTE: going with River model where PoM vertex degree ('river width') and
#       merges across domains/ranges is proportional to generalization 
#       score and 'innovation richness'. Which should be biased for selection 
#       on load() calls
#
# TODO: add re-evaluation on swap in for non-deterministic fit. landscape POMDP's
#       do this later.

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
        self.innovation_map = GlobalInnovations()

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
            return self.POMs[selection]

    def load_map(self):
        """
        getter for innovation_map used in Searcher
        """
        print('Request: innovation map')
        return self.innovation_map

    # TODO: need to serialize and store to object storage solution (S3)
    #       on each update (should async if possible this is a server after all)
    #       use fitness function serialized bytestream checksum as folder name
    #       serialize and save entire ROM. 
    def update(self, PointOfMutation):
        """
        attempt to add or merge this POM to the ROM and update GlobalInnovations
        if still relevant

        PARAMETER:
            PointOfMutation: a PointOfMutation object to be considered for
                             integrating into the RoM
        """
        print('Received: POM update attempt..')

        def mergeComparator(POM):
            # return PointOfMutation.mascot.fitness > POM and PointOfMutation.mascot.geneticDistance(
            return PointOfMutation.mascot.fitness > POM and PointOfMutation.mascot.geneticDistance(
                POM.mascot, self.disjointMetric,
                self.excessMetric, self.connectionMetric)

        def noveltyComparator(x, y):
            return x.mascot.geneticDistance(y.mascot, self.excessMetric, self.disjointMetric,
                                            self.connectionMetric) > self.radius

        # @DEPRECATED
        # noveltyComparator = lambda x, y: x.geneticDistance(
        # y, self.excessMetric, self.disjointMetric, self.connectionMetric) \
        # > self.radius

        # TODO: this is a little strange, would prefer initializing self.POMs on RoM.__init__()
        #       might rework anchored initPOM into RoM at some point.
        # NOTE:  currently using the initPOM score is 0, any diversity qualifies
        #       initPOM representation.
        if len(self.POMs) == 0:
            self.POMs.append(PointOfMutation)
            return

        # TODO: ensure or doesnt check second condition after first fails
        if PointOfMutation.parent is None or PointOfMutation.mascot.fitness > PointOfMutation.parent.mascot.fitness:
            # new POM
            if all([noveltyComparator(x, PointOfMutation) for x in self.POMs]):
                # accept the new PoM
                self.POMs.append(PointOfMutation)
            # merge/optimization PoM
            else:
                blob = filter(mergeComparator, self.POMs)
                map(PointOfMutation.merge, blob)
                self.POMs.remove(blob)

    # TODO: this may not be necessary due to manager proxy object.
    #       verify how access to GlobalInnovations is handled when
    #       passed into genepool
    def update_map(self, incomingGenepool):
        # TODO: call on POM tree-list update
        # NOTE: splitDepth data structure template:
        # Genome[split] =
        #   [node1, node2, ..]
        #   list index = splitDepth
        tmpNuclei = Nuclei()
        for g in incomingGenepool:
            tmpNuclei.readyPrimalGenes(g)
            for split in tmpNuclei.primalGenes[g]:
                # verify nodes then connections
                # TODO: look back a split depth for resultant Connection
                for con in split:
                    for outNode in con.outputNode:
                        # TODO: this requires two arguments
                        self.innovation_map.verifynode()
                        pass
                    for inNode in con.inputNode:
                        pass

        # iterate through all splits and verify connections and nodes
