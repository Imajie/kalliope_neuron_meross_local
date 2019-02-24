import hashlib
import json
import logging
import random
import socket
import string
import time

import paho
import paho.mqtt.client as mqtt

from kalliope.core.NeuronModule import NeuronModule, MissingParameterException

logging.basicConfig()
logger = logging.getLogger("kalliope")

class Meross_local_control(NeuronModule):
    """
    Class used to interact with Meross switches on a local MQTT broker
    """

    def __init__(self, **kwargs):
        super(Meross_local_control, self).__init__(**kwargs)

        self.protocols = {
            'MQTTv31': paho.mqtt.client.MQTTv31,
            'MQTTv311': paho.mqtt.client.MQTTv311
        }

        # get parameters
        self.broker_ip = kwargs.get('broker_ip', None)
        self.port = kwargs.get('port', 1883)
        self.uuid = kwargs.get('uuid', None)
        self.enabled = kwargs.get('enabled', None)
        self.qos = kwargs.get('qos', 0)
        self.retain = kwargs.get('retain', False)
        self.client_id = kwargs.get('client_id', 'kalliope')
        self.keepalive = kwargs.get('keepalive', 60)
        self.username = kwargs.get('username', None)
        self.password = kwargs.get('password', None)
        self.ca_cert = kwargs.get('ca_cert', None)
        self.certfile = kwargs.get('certfile', None)
        self.keyfile = kwargs.get('keyfile', None)
        self.protocol = kwargs.get('protocol', 'MQTTv311')
        self.tls_insecure = kwargs.get('tls_insecure', False)

        if self._is_parameters_ok():
            app_id_hash = hashlib.md5()
            app_id_hash.update(('APP%s' % self.uuid).encode('utf8'))
            self.app_id = app_id_hash.hexdigest()

            # user_id and key are assumed to be set to the UUID during switch configuration
            self.user_id = self.uuid
            self.key = self.uuid

            client_req_topic = '/appliance/%s/subscribe' % self.uuid
            client_resp_topic = '/app/%s-%s/subscribe' % (self.user_id, self.app_id)

            randomstring = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))
            idHash = hashlib.md5()
            idHash.update(randomstring.encode('utf8'))
            self.messageId = idHash.hexdigest().lower()
            self.timestamp = int(round(time.time()))

            toHash = '%s%s%s' % (self.messageId, self.key, self.timestamp)
            sigHash = hashlib.md5()
            sigHash.update(toHash.encode('utf8'))
            self.signature = sigHash.hexdigest().lower()

            self.payload = {
                    'header': {
                        'from': client_resp_topic,
                        'messageId': self.messageId,
                        'method': 'SET',
                        'namespace': 'Appliance.Control.Toggle',
                        'payloadVersion': 1,
                        'sign': self.signature,
                        'timestamp': self.timestamp
                    },
                    'payload': {
                        'channel': 0,
                        'toggle': {
                            'onoff': 1 if self.enabled else 0
                        }
                    }
                }

            # string must be converted
            self.protocol = self._get_protocol(self.protocol)

            self.client = mqtt.Client(client_id=self.broker_ip, protocol=self.protocol)

            if self.username is not None and self.password is not None:
                self.client.username_pw_set(self.username, self.password)

            if self.ca_cert is not None and self.certfile is not None and self.keyfile is not None:
                logger.debug("[meross_local_control] Active TLS with client certificate authentication")
                self.client.tls_set(ca_certs=self.ca_cert,
                                    certfile=self.certfile,
                                    keyfile=self.keyfile)
                self.client.tls_insecure_set(self.tls_insecure)

            elif self.ca_cert is not None:
                logger.debug("[meross_local_control] Active TLS with server CA certificate only")
                self.client.tls_set(ca_certs=self.ca_cert)
                self.client.tls_insecure_set(self.tls_insecure)

            try:
                self.client.connect(self.broker_ip, port=self.port, keepalive=self.keepalive)
                self.client.publish(topic=client_req_topic, payload=json.dumps(self.payload), qos=int(self.qos), retain=self.retain)
                logger.debug("[meross_local_control] Message published to topic %s: %s" % (client_req_topic, json.dumps(self.payload)))
                self.client.disconnect()

                result = {}
                self.say(result)
            except socket.error:
                logger.debug("[meross_local_control] Unable to connect to broker %s" % self.broker_ip)

    def _is_parameters_ok(self):
        if self.broker_ip is None:
            raise MissingParameterException("broker_ip")

        if self.port is not None:
            if not isinstance(self.port, int):
                try:
                    self.port = int(self.port)
                except ValueError:
                    raise InvalidParameterException("port must be an integer")

        if self.uuid is None:
            raise MissingParameterException("uuid")

        if self.enabled is None:
            raise MissingParameterException("enabled")

        if self.qos:
            if not isinstance(self.qos, int):
                try:
                    self.qos = int(self.qos)
                except ValueError:
                    raise InvalidParameterException("qos must be an integer")
            if self.qos not in [0, 1, 2]:
                raise InvalidParameterException("qos must be 0, 1, or 2")

        if self.keepalive:
            if not isinstance(self.keepalive, int):
                try:
                    self.keepalive = int(self.keepalive)
                except ValueError:
                    raise InvalidParameterException("keepalive must be an integer")

        if self.username is not None and self.password is None:
            raise MissingParameterException("password must be set when username is present")
        if self.username is None and self.password is not None:
            raise MissingParameterException("username must be set when password is present")

        if self.protocol:
            if self.protocol not in self.protocols.keys():
                raise InvalidParameterException("protocol")

        # if the user set a certfile, the key and ca cert must be set to
        if self.certfile is not None and self.keyfile is None:
            raise MissingParameterException("keyfile must be set when certfile is present")
        if self.certfile is None and self.keyfile is not None:
            raise MissingParameterException("certfile must be set when keyfile is present")

        if self.certfile is not None and self.keyfile is not None:
            if self.ca_cert is None:
                raise MissingParameterException("ca_cert must be set when keyfile and certfile are present")

        return True

    def _get_protocol(self, protocol):
        """
        Return the right code depending on the given string protocol name
        :param protocol: string name of the protocol to use.
        :return: integer
        """
        return self.protocols[protocol]
