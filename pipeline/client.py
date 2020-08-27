from pipeline.page import page


# TODO: try this with XOR and an actual gradient
# TODO: make this a template and extract this to tests module
def fit(x):
    x.fitness = 2
    return x


if __name__ == '__main__':
    p = page(10, '127.0.0.1', fit, 10)
    p.exec()
