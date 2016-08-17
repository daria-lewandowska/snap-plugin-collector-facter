from modules import utils
from modules.logger import log
from unittest import TextTestRunner

import sys
import unittest

class FacterCollectorLargeTest(unittest.TestCase):

    def setUp(self):
        # set and download required binaries (snapd, snapctl, plugins)
        self.binaries = utils.set_binaries()
        utils.download_binaries(self.binaries)

        log.debug("Starting snapd")
        self.binaries.snapd.start()
        if not self.binaries.snapd.isAlive():
            self.fail("snapd thread died")

        log.debug("Waiting for snapd to finish starting")
        if not self.binaries.snapd.wait():
            log.error("snapd errors: {}".format(self.binaries.snapd.errors))
            self.binaries.snapd.kill()
            self.fail("snapd not ready, timeout!")

    def test_facter_collector_plugin(self):
        # load facter collector
        loaded = self.binaries.snapctl.load_plugin("snap-plugin-collector-facter")
        self.assertTrue(loaded, "facter collector loaded")

        # check available metrics, plugins and tasks
        metrics = self.binaries.snapctl.list_metrics()
        plugins = self.binaries.snapctl.list_plugins()
        tasks = self.binaries.snapctl.list_tasks()
        self.assertGreater(len(metrics), 0, "Metrics available {} expected {}".format(len(metrics), 0))
        self.assertEqual(len(plugins), 1, "Plugins available {} expected {}".format(len(plugins), 1))
        self.assertEqual(len(tasks), 0, "Tasks available {} expected {}".format(len(tasks), 0))

    def tearDown(self):
        log.debug("Stopping snapd thread")
        self.binaries.snapd.stop()
        if self.binaries.snapd.isAlive():
            log.warn("snapd thread did not died")

if __name__ == "__main__":
    test_suite = unittest.TestLoader().loadTestsFromTestCase(FacterCollectorLargeTest)
    test_result = TextTestRunner().run(test_suite)
    sys.exit(len(test_result.failures))