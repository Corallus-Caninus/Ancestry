import random as rand
from copy import deepcopy


class PointOfMutation:
    """
    a tree of genepool snapshots used for monte carlo tree search.

    PARAMETERS:
        snapshot: a snapshot of the genepool that defines this Point of Mutation
        mascot: the highest scoring member that justifies this Point of Mutation
    """

    def __init__(self, snapshot, mascot, parent):
        assert mascot in snapshot, \
            "mascot must be a member of the defining genepool snapshot"

        self.snapshot = snapshot
        self.mascot = mascot

        # set edges for tree structure
        if parent is not None:
            self.parent = parent
            self.parent.children.append(self)

        self.children = []

    def __add__(self, other):
        self.merge(other)

    # TODO: class method for anchored initPOM?
    def merge(self, otherPoM):
        """
        merge this Point of Mutation with another, destroying both PoMs
        and increasing the edges of the resultant PoM.

        PARAMETERS:
            otherPoM: the other PoM to be merged into.
        """
        # TODO: remove the old PoMs from river list. This
        #       only handles PoM trees

        # TODO: mess around with this for different MC tree representations.
        #       this is the simplest but most lossy and has no edge attribute
        #       so differing hyperparameters and timeouts break complexity
        #       edge proportionality.
        if self.parent is otherPoM:
            self.parent = self.parent.parent

        self.children.extend(otherPoM.children)
        for child in self.children:
            child.parent = self

    def swap(self, population):
        """
        swap in this Point of Mutation

        PARAMETERS:
            population: the size of the genepool that is requesting this PoM
        RETURNS:
            genepool: a list of genomes the size of population generated from snapshots
        """
        genepool = []

        if population != len(self.snapshot):
            while len(genepool) < population:
                genepool.append(deepcopy(self.snapshot[rand.randint(0, len(self.snapshot - 1))]))
        else:
            genepool = deepcopy(self.snapshot)

        return genepool
