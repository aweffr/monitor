from __future__ import print_function
import os
import sys
import inspect

if __name__ == "__main__":
    file_path = inspect.getfile(inspect.currentframe())
    cwd = os.path.dirname(file_path)
    os.chdir(cwd)
    print("Now cwd is:", os.getcwd())

    f = open('success.log', 'w')
    f.close()
    import app
    app.monitor_run()
