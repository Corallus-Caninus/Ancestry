import random as rand
import unittest
from pipeline.page import page


def xor(solutionList):
    """
    0 0 | 0 1 | 1 0 | 1 1
     0   |   1  |   1  |  0

    """
    if solutionList is [0, 0]:
        return 0
    elif solutionList is [0, 1]:
        return 1
    elif solutionList is [1, 0]:
        return 0
    elif solutionList is [1, 1]:
        return 1
    else:
        raise Exception("wrong values sent to xor")


def myFunc(genome):
    """
    takes a Genome returns Genome with fitness associated
    """
    numTries = 50
    score = 0

    # needs to be random to prevent memorizing order of input
    for _ in range(0, numTries):
        entry1 = rand.randint(0, 1)
        entry2 = rand.randint(0, 1)

        output = genome.forwardProp([entry1, entry2])[0]

        if output >= 0.5:
            if entry1 == 1 or entry2 == 1:
                # one
                if entry1 != 1 and entry2 != 1:
                    score += 1
        elif output < 0.5 and entry1 == 1 and entry2 == 1:
            score += 1
        elif output < 0.5 and entry1 == 0 and entry2 == 0:
            score += 1

    score = score / numTries
    # return score
    genome.fitness = score
    return genome


class TestXOR(unittest.TestCase):
    def test_xor(self):
        # TODO: test name of service
        p = page(10, 'ancestry-pipeline', myFunc, 10)
        #p = page(10, '127.0.0.1', myFunc, 10)
        p.exec()


if __name__ == '__main__':
    unittest.main()
