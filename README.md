# Meross Local Control

## Synopsis

This neuron allows for control of [Meross](https://meross.com) smart plugs. Based on the mqtt\_publisher in kallipoe.

## Installation

```bash
kalliope install --git-url https://github.com/Imajie/kalliope_neuron_meross_local.git
```

### Options
| parameter     | required | type   | default  | choices           | comment                                                        |
|-------------  |----------|--------|----------|-------------------|----------------------------------------------------------------|
| broker\_ip    | Yes      | String | None     |                   | The MQTT broker hostname or IP address                         |
| port          | No       | Int    | 1883     |                   | The port for the MQTT broker                                   |
| uuid          | Yes      | String | None     |                   | The UUID of the switch to control                              |
| enabled       | Yes      | Bool   | None     |                   | True to turn on the switch, False, to turn off                 |
| toggleX       | No       | Bool   | False    |                   | True if this switch uses ToggleX instead of Toggle for control |
| qos           | No       | Int    | 0        | 0, 1, 2           | The desired MQTT QoS level                                     |
| retain        | No       | Bool   | False    |                   | True if the message should be retained by the MQTT broker      |
| client\_id    | No       | String | kalliope |                   | The string to use for the client\_id for MQTT                  |
| keepalive     | No       | Int    | 60       |                   | The time in seconds to send keepalive pings                    |
| username      | No       | String | None     |                   | The username if authentication is required for MQTT            |
| password      | No       | String | None     |                   | The password if authentication is required for MQTT            |
| ca\_cert      | No       | String | None     |                   | Path to the cacert if MQTT uses a self-signed CA               |
| certfile      | No       | String | None     |                   | Path to the client cert to use to authenticate to MQTT         |
| keyfile       | No       | String | None     |                   | Path to the client keyfile to use to communicate to MQTT       |
| protocol      | No       | String | MQTTv311 | MQTTv31, MQTTv311 | The MQTT protocol version to use                               |
| tls\_insecure | No       | Bool   | False    |                   | Set to True to not validate the MQTT certificate               |

### Return Values

None

## Synapse Examples
```yml
  - name: 'light-on'
    signals:
      - order: 'turn on the light'
    neurons:
      - meross_local_control:
          broker_ip: '1.2.3.4'
          port: '1883'
          uuid: '12345678909abcdef'
          enabled: True

  - name: 'light-off'
    signals:
      - order: 'turn off the light'
    neurons:
      - meross_local_control:
          broker_ip: '1.2.3.4'
          port: '1883'
          uuid: '12345678909abcdef'
          enabled: False
```
