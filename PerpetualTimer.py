from threading import Timer


class PerpetualTimer():

    def __init__(self, t, hFunction, arg):
        self.t = t
        self.hFunction = hFunction
        self.arg = arg
        self.hFunction(arg)
        self.thread = Timer(self.t, self.handle_function, [self.arg])

    def handle_function(self, args):
        self.hFunction(args)
        self.thread = Timer(self.t, self.handle_function, [self.arg])
        self.thread.start()

    def start(self):
        self.thread.start()

    def cancel(self):
        self.thread.cancel()
