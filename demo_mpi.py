from mpi4py import MPI
from mpi4py.futures import MPICommExecutor, as_completed
comm = MPI.COMM_WORLD

import numpy as np
import time
from distribute_tasks import distribute_tasks


##smoothing an image (CPU-bound)
def smooth_img(job_id):
    print(f'job {job_id} start...', flush=True)

    ny, nx = 2000, 2000
    img = np.random.normal(0, 1, (ny, nx))

    new_img = np.zeros(img.shape)
    ny, nx = img.shape
    for j in range(1, ny-1):
        for i in range(1, nx-1):
            new_img[j, i] = (img[j-1, i-1] + img[j-1, i] + img[j-1, i+1] +
                             img[j,   i-1] + img[j,   i] + img[j,   i+1] +
                             img[j+1, i-1] + img[j+1, i] + img[j+1, i+1]) / 9

    print(f'job {job_id} finish', flush=True)


def parallel_with_comm_executor():
    t0 = time.time()

    with MPICommExecutor(comm, root=0) as executor:
        futures = []
        for job_id in range(200):
            future = executor.submit(smooth_img, job_id)
            futures.append(future)

    for future in as_completed(futures):
        try:
            result = future.result()
        except Exception as e:
            print(f'Error: {e}')

    comm.Barrier()
    for future in futures:
        assert future.done()

    t1 = time.time()
    if comm.Get_rank() == 0:
        print(f'elapsed time: {t1-t0} s')


def parallel_with_distribute_tasks():
    t0 = time.time()

    job_list = np.arange(200)

    job_list_pid = distribute_tasks(comm, job_list)
    for job_id in job_list_pid[comm.Get_rank()]:
        smooth_img(job_id)

    comm.Barrier()
    t1 = time.time()
    if comm.Get_rank() == 0:
        print(f'elapsed time: {t1-t0} s')


if __name__ == '__main__':
    # parallel_with_comm_executor()
    parallel_with_distribute_tasks()

