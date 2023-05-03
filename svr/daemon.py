#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 tombraid@snu.ac.kr
# All right reserved.
#

"""
    Daemon을 만들어주는 클래스를 정의함
"""

import sys
import time
import os
import atexit
import logging
import logging.handlers
import signal

class Runner(object):
    """
    Daemon이 작동시키는 클래스의 기본 골격
    """
    def setlogger(self, logger):
        """
        로거를 세팅함
        :param logger: 로깅을 해주는 로거
        """
        self._logger = logger

    def initialize(self):
        """
        초기화를 수행함
        """
        self._logger.debug("initialized....")

    def finalize(self):
        """
        작동을 마무리함
        """
        self._logger.debug("finalized....")

    def run(self, debug=False):
        """
        작동함
        """
        self._logger.debug("running....")

    def stop(self):
        """
        작동을 중지함
        """
        self._logger.debug("stopping....")

def getlogger(pname):
    import logging
    import logging.handlers

    logger = logging.getLogger(pname)
    logger.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s')
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)
    fileHandler = logging.handlers.RotatingFileHandler("/var/log/" + pname + ".log", maxBytes=5000000, backupCount=5)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)

    return logger

class Daemon:
    """
    A generic daemon class.
    """
    def __init__(self, pname, runner, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        """
        Deamon Constructor
        :param pname: process name
        :param runner: Runner instance
        :param stdin: redirection stdin to 
        :param stdout: redirection stdout to
        :param stderr: redirection stderr to
        """
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = "/var/run/" + pname + ".pid"
        self.runner = runner
        self.isdaemon = False
        self.pname = pname

        signal.signal(signal.SIGINT, self.terminate)
        signal.signal(signal.SIGTERM, self.terminate)

        self._logger = getlogger(pname)
        self.runner.setlogger(self._logger)

    def daemonize(self):
        """
        데몬으로 변경함

        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                #sys.exit(0)
                return False
        except OSError as e:
            self._logger.warning("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # decouple from parent environment
        #os.chdir("/")
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError as e:
            self._logger.warning("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        self._logger.warning("Entering daemon mode (" + str(os.getpid()) + ")\n")
        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(self.stdin, 'r')
        so = open(self.stdout, 'a+')
        se = open(self.stderr, 'a+')
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        pf = open(self.pidfile, 'w+')
        pf.write("%s\n" % pid)
        pf.close()
        self.isdaemon = True
        return True

    def delpid(self):
        """
        remove pid file
        """
        os.remove(self.pidfile)

    def checkpid(self, pid):        
        """ Check For the existence of a unix pid. """
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        else:
            return True

    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        self._logger.warning("Check for a pidfile to see if the daemon already runs\n")
        self._logger.warning(self.pidfile + "\n")
        try:
            pf = open(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
            if self.checkpid(pid) is False:
                pid = None
        except IOError:
            pid = None

        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            self._logger.warning(message % self.pidfile)
            sys.exit(1)

        # Start the daemon
        if self.daemonize():
            self.run()
 
    def stop(self):
        """
        Stop the daemon
        """
        self.runner.stop()
        #self.stop()

    def dstop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            pf = open(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
       
        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            self._logger.warning(message % self.pidfile)
            return # not an error in a restart
 
        # Try killing the daemon process       
        try:
            self._logger.info("Trying to stop a process " + str(pid)) 
            self._logger.info("It might take few seconds.")
            os.kill(pid, signal.SIGTERM)
            for _ in range(30):
                if self.checkpid(pid) is False:
                    break
                time.sleep(1)

            if self.checkpid(pid):
                self._logger.info("The process still remains.")
                os.kill(pid, signal.SIGKILL)
        except OSError as err:
            err = str(err)
            if err.find("No such process") <= 0:
                self._logger.warning(err)

        if os.path.exists(self.pidfile):
            os.remove(self.pidfile)

    def terminate(self, signum, frame):
        """
        terminate the daemon
        :param signum: not used
        :param frame:  not used
        """
        self._logger.info("process killed.")
        self.stop()
        #sys.exit(1)
 
    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    def run(self, debug=False):
        """
        Execute a runner
        """
        self.runner.initialize()
        self.runner.run(debug)
        self.runner.finalize()


if __name__ == '__main__':  
    if len(sys.argv) != 2:
        print("Usage : python daemon.py [start|stop|restart]")
        sys.exit(2)

    mode = sys.argv[1]
    runner = Runner ()
    daemon = Daemon('pydaemon', runner)
    if 'start' == mode:
        daemon.start()
    elif 'stop' == mode:
        daemon.dstop()
    elif 'restart' == mode:
        daemon.restart()
    else:
        print("Unknown command")
        sys.exit(2)
    sys.exit(0)

