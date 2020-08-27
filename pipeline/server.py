from multiprocessing.managers import BaseManager

from RiverOfMutation.ROM import RiverOfMutations

# TODO:  if manager continues to throw errors, rewrite server, Searcher, client
#       and ROM to take serialized/pickled POMs and process them internally 
#       since ROM is by design distributable at POM level if nothing else.

if __name__ == '__main__':
    # TODO: read config for address, authkey and hyperparameters
    # TODO: double splat a dictionary for keyword
    # TODO: read in from object storage
    # TODO: create a class this should be a class for SaaS configuration

    distanceParams = {'radius': 10, 'excess_metric': 1,
                      'disjoint_metric': 0.5, 'connection_metric': 0.5}
    head_stream = RiverOfMutations(**distanceParams)

    # class irrigator(BaseManager): pass
    # returns a copy of the river object when called.
    BaseManager.register('River', callable=lambda: head_stream)

    # TODO: verify service works in kubernetes then extract to configuration/kwargs
    manager = BaseManager(address=('', 5000), authkey='bada'.encode())
    print('serving ROM: {}..'.format(dir(head_stream)))
    manager.get_server().serve_forever()
    print('server shutdown.')
