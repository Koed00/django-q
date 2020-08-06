import numpy

from django_q.tasks import async_iter, result


# the estimation function
def parzen_estimation(x_samples, point_x, h):
    k_n = 0
    for row in x_samples:
        x_i = (point_x - row[:, numpy.newaxis]) / h
        for row in x_i:
            if numpy.abs(row) > (1 / 2):
                break
        else:
            k_n += 1
    return h, (k_n / len(x_samples)) / (h ** point_x.shape[1])


def parzen_async():
    mu_vec = numpy.array([0, 0])
    cov_mat = numpy.array([[1, 0], [0, 1]])
    sample = numpy.random.multivariate_normal(mu_vec, cov_mat, 10000)
    widths = numpy.linspace(1.0, 1.2, 100)
    x = numpy.array([[0], [0]])
    # async_task them with async_task iterable
    args = [(sample, x, w) for w in widths]
    result_id = async_iter(parzen_estimation, args, cached=True)
    # return the cached result or timeout after 10 seconds
    return result(result_id, wait=10000, cached=True)
