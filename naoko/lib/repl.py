# -*- coding: utf-8 -*-

import code
import socket
import sys
import threading

BANNER = '------------Naoko REPL--------------'
PROMPT_STRING = 'Naoko via TCP>'

class ReplConn(object):
    def __init__(self, conn):
        self.conn = conn

    def write(self, s):
        self.conn.send(s.encode("utf-8"))

    def read(self, prompt):
        self.conn.send(prompt)
        return self.conn.recv(4096)

    def flush(self):
        return


class Repl(threading.Thread):
    def __init__(self, port, host='localhost', locals={}):
        self.closing = False
        sys.ps1      = PROMPT_STRING

        self.port    = port
        self.host    = host
        self.socket  = socket.socket(socket.AF_INET, 
                                    socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(1)
        self.console = code.InteractiveConsole(locals)
        super(Repl, self).__init__(target=self._replLoop)

        # This thread is relatively self contained and no exceptions
        # should bubble up to an external thread. Be warned the program
        # may not exit if there's a live socket. (it probably will though
        # as the below loop has no exception handler)
        self.start()
      
    def _replLoop(self):
        while not self.closing:
            (conn, addr) = self.socket.accept()
            repl = ReplConn(conn)
            sys.stdout   = sys.stderr = repl
            self.console.raw_input = repl.read
            self.console.interact(BANNER)

    def close(self):
        self.closing = True
        self.socket.settimeout(0)
        self.socket.close()

if __name__ == '__main__':
    HOST = 'localhost'
    PORT = 5001
    Repl(PORT, HOST)
