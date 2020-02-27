from multiprocessing.managers import BaseManager
from ROM import RiverOfMutations

if __name__ == '__main__':
    #TODO: read config for address, authkey and hyperparameters
    
    distanceParams = [10, 1, 0.5, 0.5]
    class irrigator(BaseManager): pass
    irrigator.register('River', RiverOfMutations(*distanceParams))

    # manager = BaseManager(address = ('', 5000), authkey='bada'.encode())
    manager = irrigator(address = ('', 5000), authkey='bada'.encode())
    manager.get_server().serve_forever()

    #@DEPRECATED needs testing
    # manager.register('swap_in', callable = self.swap_in)
    # manager.register('update', callable = self.update)
