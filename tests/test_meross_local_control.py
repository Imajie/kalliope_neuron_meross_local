import json
import unittest

import mock
from kalliope.core.NeuronModule import MissingParamterException
from kalliope.neurons.meross_local_control import Meross_local_control

class TestMerossLocalControl(unittest.TestCase):
    def setUp(self):
        self.uuid = '1234567890abcdef'
        self.broker = 'localhost'

    def testMissingParameters(self):
        def run_test(parameters_to_test):
            with self.assertRaises(MissingParameterException):
                Meross_local_control(**parameters_to_test)

        # Fail without any parameters
        run_test(dict())

        # Fail without broker
        run_test({
            'uuid': self.uuid,
            'enabled': True
            })

        # Fail without UUID
        run_test({
            'broker_ip' : self.broker,
            'enabled': True
            })

        # Fail without enabled
        run_test({
            'broker_ip' : self.broker,
            'uuid': self.uuid
            })
