from . import Plugin


class CollectdPlugin(Plugin):
    def __init__(self, config):
        if hasattr(config, 'collectd_prefix'):
            prefix = config.collectd_prefix
        else:
            prefix = '^collectd\.'

        self.targets = [
            {
                'match': prefix + '(?P<server>[^\.]+)\.(?P<collectd_plugin>cpu)[\-\.](?P<core>[^\.]+)\.cpu[\-\.](?P<type>[^\.]+)$',
                'target_type': 'gauge_pct',
                'tags': {
                    'unit': 'Jiff',
                    'what': 'cpu_usage'
                }
            },
            {
                'match': prefix + '(?P<server>.+?)\.(?P<collectd_plugin>load)\.load\.(?P<wt>.*)$',
                'target_type': 'gauge',
                'configure': lambda self, target: self.fix_load(target)
            },
            {
                'match': prefix + '(?P<server>[^\.]+)\.interface[\-\.](?P<device>[^\.]+)\.if_(?P<wt>[^\.]+)\.(?P<dir>[^\.]+)$',
                'target_type': 'counter',
                'tags': {'collectd_plugin': 'network'},
                'configure': lambda self, target: self.fix_network(target)
            },
            {
                'match': prefix + '(?P<server>[^\.]+)\.memory\.memory[\-\.](?P<type>[^\.]+)$',
                'target_type': 'gauge',
                'tags': {
                    'unit': 'B',
                    'where': 'system_memory'
                }
            },
            {
                'match': prefix + '(?P<server>[^\.]+)\.df[\-\.](?P<mountpoint>[^\.]+)\.df_complex[\-\.](?P<type>[^\.]+)$',
                'target_type': 'gauge',
                'tags': {'unit': 'B'}
            },
            {
                'match': prefix + '(?P<server>[^\.]+)\.(?P<collectd_plugin>disk)[\-\.](?P<device>[^\.]+)\.disk_(?P<wt>[^\.]+)\.(?P<operation>[^\.]+)$',
                'configure': lambda self, target: self.fix_disk(target)
            },
            {
                'match': prefix + '(?P<server>.+?)\.(?P<collectd_plugin>irq)\.irq[\-\.](?P<wt>.*)$',
                'target_type': 'counter',
                'tags': {
                    'unit': 'calls',
                    'what': 'irq_calls'
                }

            },
            {
                'match': prefix + '(?P<server>.+?)\.(?P<collectd_plugin>processes)\.ps_state[\-\.](?P<state>.*)$',
                'target_type': 'gauge',
                'tags': {
                    'unit': 'procs',
                    'what': 'procs_in_state'
                }

            },
            {
                'match': prefix + '(?P<server>.+?)\.(?P<collectd_plugin>processes)\.(?P<value>fork_rate)$',
                'target_type': 'counter',
                'tags': {
                    'unit': 'procs',
                    'what': 'fork_rate'
                }

            },
            {
                'match': prefix + '(?P<server>[^\.]+)\.swap\.swap[\-\.](?P<type>[^\.]+)$',
                'target_type': 'gauge',
                'tags': {
                    'unit': 'B',
                    'where': 'swap'
                }
            },
            {
                'match': prefix + '(?P<server>[^\.]+)\.swap\.swap_io[\-\.](?P<dir>[^\.]+)$',
                'target_type': 'counter',
                'tags': {
                    'unit': 'B',
                    'where': 'swap_io'
                }
            },
            {
                'match': prefix + '(?P<server>.+?)\.(?P<collectd_plugin>tcpconns)[\-\.](?P<port>\d+)[\-\.]local\.tcp_connections[\-\.](?P<state>.*)$',
                'target_type': 'gauge',
                'tags': {
                    'unit': 'connections',
                    'what': 'tcp_connections_in_state'
                }

            },
            {
                'match': prefix + '(?P<server>.+?)\.(?P<collectd_plugin>contextswitch)\.(?P<value>contextswitch)$',
                'target_type': 'counter',
                'tags': {
                    'unit': 'fork/s',
                    'what': 'contextswitch'
                }

            },
            {
                'match': prefix + '(?P<server>.+?)\.(?P<collectd_plugin>users)\.(?P<value>users)$',
                'target_type': 'gauge',
                'tags': {
                    'unit': 'users',
                    'what': 'users_logged'
                }

            },
            {
                'match': prefix + '(?P<server>.+?)\.(?P<collectd_plugin>entropy)\.(?P<value>entropy)$',
                'target_type': 'gauge',
                'tags': {
                    'unit': 'bits',
                    'what': 'entropy'
                }

            },
            {
                'match': prefix + '(?P<server>.+?)\.(?P<collectd_plugin>conntrack)\.(?P<value>conntrack)$',
                'target_type': 'gauge',
                'tags': {
                    'unit': 'entries',
                    'what': 'conntrack'
                }

            },
        ]
        super(CollectdPlugin, self).__init__(config)

    def fix_disk(self, target):
        wt = {
            'merged': {
                'unit': 'Req',
                'type': 'merged'
            },
            'octets': {
                'unit': 'B'
            },
            'ops': {
                'unit': 'Req',
                'type': 'executed'
            },
            'time': {
                'unit': 'ms'
            }
        }
        target['tags'].update(wt[target['tags']['wt']])

        if self.config.collectd_StoreRates:
            target['tags']['target_type'] = 'rate'
            target['tags']['unit'] = target['tags']['unit'] + "/s"
        else:
            target['tags']['target_type'] = 'counter'

        del target['tags']['wt']

    def fix_load(self, target):
        human_to_computer = {
            'shortterm': '01',
            'midterm': '05',
            'longterm': '15'
        }
        target['tags']['unit'] = 'load'
        target['tags']['type'] = human_to_computer.get(target['tags']['wt'], 'unknown')
        del target['tags']['wt']

    def fix_network(self, target):
        dirs = {'rx': 'in', 'tx': 'out'}
        units = {'packets': 'Pckt', 'errors': 'Err', 'octets': 'B'}

        if self.config.collectd_StoreRates:
            target['tags']['target_type'] = 'rate'
            target['tags']['unit'] = units[target['tags']['wt']] + "/s"
        else:
            target['tags']['target_type'] = 'counter'
            target['tags']['unit'] = units[target['tags']['wt']]

        target['tags']['direction'] = dirs[target['tags']['dir']]
        del target['tags']['wt']
        del target['tags']['dir']

# vim: ts=4 et sw=4:
