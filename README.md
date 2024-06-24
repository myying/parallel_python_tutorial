## Tutorial on parallel programming in Python

### Some background on processes

A CPU has several cores, each is able to execute some instructions to perform computation. When you run a program it is typical that a CPU core creates a `process` that executes the instructions from the program. A core can also be multitasking, meaning that it creates `threads` for sequences of instructions that can be run almost simultaneously.

On Linux, you can try `./main.sh`, it calls the `run_job.sh` script several times and run these in the background `./run_job.sh $job_id &`. The `&` is Linux syntax to run a program in the background. You can use `fg` to bring programs in the background back to the foreground. In the command line, a program running in the foreground will have to wait till completion for other programs to run. You can send signals to a foreground program by keyboard interruption (Ctrl+C or Ctrl+Z), or a background program by `kill -s SIG pid`. To monitor programs running in the background you can use `ps auf` (`pstree` in MacOS), or using the `top`/`htop` program.

Programs that are heavy in computation (CPU-bound) will take most of the time using the CPU core running instructions, you typically see near 100% CPU when it's running. Programs that are doing more file I/O or web communication (I/O-bound) will take most of the time waiting for the slow data transfer, typically not full CPU usage. To parallelize a program that is CPU-bound, you have to involve more CPU cores, while for I/O-bound program you can use multiple threads one the single CPU core to achieve concurrency.

The Python interpreter now has a Global Interpreter Lock (GIL), which prevents threads to run simultaneously. This limits the threading in Python to only I/O-bound tasks. But Python program can still use multiple processes to achieve parallelism. In fact there are so many libraries in Python for parallelization, it is indeed quite confusing.


### Some built-in modules in Python for parallel programs

The `subprocess` module provides tools to start a child process from the current process. It is a bit like running a program "in the background", `subprocess.run(cmd, shell=True)` and `os.system(cmd)` both run `cmd` in a subprocess through the shell. `p = subprocess.Popen(cmd, shell=True)` gives more control to the process `p`, so that you can send signal to it and capture its runtime stdout and stderr.

The `asyncio` module allows functions to be run concurrently, use key words `async` and `await` to define the behavior of each function and coordinate their runtime execution. The `threading` module provides a higher-level framework for starting multiple threads, `th = threading.Thread(target=func)`, `th.start()`, `th.join()`, using `Lock()` to make sure thread-safe access to data in runtime.

The `multiprocessing` module provides alternative parallelization of functions using `subprocess` so that no lock is needed, it is suitable for CPU-bound tasks. To start a process, `p = multiprocessing.Process(target=func, args=(...))`, `p.start()`, `p.join()`. The `multiprocessing.shared_memory` provides some shared memory interprocess communication.


### Some high-level/third-party modules

In most application scenarios, you can avoid coding `async` functions or creating process/thread yourself, but rather using some high-level modules that are already prepared for the multi-tasking.

`concurrent.futures` module provides `ProcessPoolExecutor` and `ThreadPoolExecutor` for parallel execution of a list of tasks using multiprocessing and threading.
See example in `demo_concurrent_futures.ipynb`. Note that `multiprocessing` is based on shared-memory parallelism (in OpenMP, on one computer), it cannot utilize multiple compute nodes in a big cluster.

`mpi4py` is a wrapper to the classic MPI library to allow truly distributed-memory parallelism in high performance computer cluster to scale to even larger amount of CPU cores. Speed-up can be achieved by partitioning the task list by `distribute_tasks`, and each processor runs a subset of the tasks. See the example in `demo_mpi.py` using `parallel_with_distribute_tasks()`.
The `mpi4py.futures.MPICommExecutor` also provide a high-level module to spawn the tasks to all the available processors in the communicator.
`mpi4py.MPI` also allows you to perform interprocess communication, such as `comm.send`, `comm.recv`, `comm.allreduce`, `comm.gather`, etc.


### Other ways to speed up python code

- Use third party library with built-in parallelism to replace your slow code.

    For example, `numpy` `scipy` is built with BLAS/LAPACK for linear algebra that is very efficient. For FFT, `numpy.fft` is slightly slower than `pyFFTW` using the FFTW library. For some matrix operation, `numpy.einsum` provides many fast implementation, no need to write for loops to sum/average and try to optimize yourself.

    So, search for existing libraries before writing your code! There may already be many options out there.

- Pre-compile the slow code at runtime to accelerate it

    CPU: use `numba.njit` to accelerate a function, although it limits the function from using pythonic features such as classes.

    GPU: `cupy` is a GPU accelerated version of `numpy`; `numba.cuda.jit` can compile a function to utilize the CUDA library on GPUs. A lot of machine learning libraries are built upon the CUDA library.

- Use `dask.distributed` to build a cluster and automate the parallelization

    Dask setup a few workers in a cluster so that they can participate the computation to achieve parallelism. The workers can be a local CPU core, a remote computer CPU core, or whatever. It is flexible to add new workers even in runtime. But be aware that it takes some time to configure...for different machines.

    Automatic generation of parallel algorithm (graph), you don't need to think about how to parallelize your code, if you have a for loop, it will distribute it onto the workers; if there is a collective operation (tranpose, sum, or other convolution), the optimal graph of dependency will be computed. Note that this flexibility also requires overhead, so it might not be the most efficient way...

    You can visualize resource usage during runtime, in jupyter-lab you can install `dask_labextension` to see the worker status and progress, this is useful for debugging? But I feel it's a bit overkill.

Suggestion: consider how much time you're willing to spend on creating the program and how many times the program will be run, so that you have a good balance of cost and benefit. So choose the best tool to do your job and have fun parallel programming!
