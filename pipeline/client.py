from pipeline.page import page


# NOTE: this is a template
def fit(x):
    x.fitness = 2
    return x


if __name__ == '__main__':
    p = page(10, '127.0.0.1', fit, 10)
    p.exec()
