# ovirt-imageio
# Copyright (C) 2018 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

from __future__ import absolute_import
from __future__ import division

import sys
import time


class ProgressBar(object):

    def __init__(self, size=0, output=sys.stdout, step=0.1, width=79):
        """
        Argumnets:
            size (int): total number of bytes. If size is unknown when
                creating, progress value is not displayed. The size can be set
                later to enable progress display.
            output (fileobj): file to write progress to (default sys.stdout).
            step (float): mininum progress update interval in seconds (default
                0.1 seconds).
            width (int): width of progress bar in characters (default 79)
        """
        self.size = size
        self.output = output
        self.step = step
        # TODO: use current terminal width instead.
        self.width = width
        self.start = time.time()
        self.next = 0
        self.done = 0

        # The first update can take some time.
        self.update(0)

    def update(self, n):
        """
        Increment the progress by n bytes.

        Should be called for every successful transfer, with the number of
        bytes transfer. The number of bytes transfered is updated on every
        call, but the progress is updated only if step seconds have passed
        since the last update.

        Note: this interface is compatible with tqdm[1], to allow user to use
        different progress implementations.

        [1] https://github.com/tqdm/tqdm#manual
        """
        self.done += n
        now = time.time()
        if now < self.next:
            return

        self.next = now + self.step
        self._draw(now)

    def close(self):
        # If we wrote progress, we need to draw the last progress line.
        if self.done > 0:
            self._draw(time.time(), last=True)

    def _draw(self, now, last=False):
        elapsed = now - self.start

        if self.size:
            progress = "%6.2f%%" % (self.done / self.size * 100)
        else:
            progress = "-------"

        line = "[ %s ] %s, %.2f seconds, %s/s" % (
            progress,
            humansize(self.done),
            elapsed,
            humansize(self.done / elapsed if elapsed else 0),
        )

        line = line.ljust(self.width, " ")

        # Using "\r" moves the cursor to the first column, so the next progress
        # will overwite this one. If this is the last progress, we use "\n" to
        # move to the next line. Otherwise, the next shell prompt will include
        # part of the old progress.
        end = "\n" if last else "\r"

        self.output.write(line + end)
        self.output.flush()

    def __enter__(self):
        return self

    def __exit__(self, t, v, tb):
        self.close()


def humansize(n):
    for unit in ("bytes", "KiB", "MiB", "GiB", "TiB", "PiB"):
        if n < 1024:
            break
        n /= 1024
    return "{:.{precision}f} {}".format(
        n, unit, precision=0 if unit == "bytes" else 2)
