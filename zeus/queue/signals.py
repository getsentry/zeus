from blinker import signal

task_prerun = signal("task_prerun")
task_postrun = signal("task_postrun")

worker_process_init = signal("worker_process_init")
