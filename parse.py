import csv
import sys
import yaml
import os
import re

NRI_HEADER_INT = "integration"
NRI_HEADER_METRIC = "metric_name"
NRI_HEADER_TYPE = "metric_type"
NRI_HEADER_ENABLED = "metric_enabled"
NRI_HEADER_DESC = "metric_description"


def base_dir():
    return os.path.dirname(os.path.realpath(__file__))


def load_conf_file():
    with open("{}/config.yaml".format(base_dir()), "r") as f:
        return yaml.safe_load(f)


CONFIG = load_conf_file()


class NRMetricInfo:
    def __init__(self, integration, metric_name, metric_type, metric_enabled, metric_description):
        self.event = None
        self.integration = integration
        self.name = metric_name
        self._type = metric_type
        self.enabled = metric_enabled
        self.description = metric_description


class NRDashboardTab:
    def __init__(self, name, metrics):
        self.name = name
        self.metrics = metrics


def open_file(filename):
    try:
        return open(filename, 'r')
    except Exception as e:
        raise Exception(e)


def csv_reader(filename):
    try:
        return csv.DictReader(open_file(filename), delimiter=',')
    except Exception as e:
        raise Exception(e)


def parse_metrics(data):
    return [NRMetricInfo(i[NRI_HEADER_INT], i[NRI_HEADER_METRIC],
                         i[NRI_HEADER_TYPE], i[NRI_HEADER_ENABLED], i[NRI_HEADER_DESC]) for i in data]


def get_metric_by_prefix(event, metrics, prefix):
    output = []

    for m in metrics:
        regex = r"^{}".format(prefix)
        if re.match(regex, m.name):
            m.event = event
            output.append(m)

    return output


def prepare_tabs(parsed_tabs, parsed_metrics):
    tabs = []

    for tab in parsed_tabs:
        base_event = tab['event']
        tab_metrics = []

        for metric in tab['metrics']:
            spec_event = None

            if metric.get('event'):
                spec_event = metric['event']

            event = spec_event if spec_event is not None else base_event
            tab_metrics = tab_metrics + get_metric_by_prefix(event, parsed_metrics, metric['name'])
            spec_event = None

        tabs.append(NRDashboardTab(tab['name'], tab_metrics))

    return tabs


def main():
    tabs = prepare_tabs(CONFIG['tabs'], parse_metrics(csv_reader(arg_filename)))

    for i in tabs:
        print(i.name)
        for j in i.metrics:
            print(j.event, j.name)


if __name__ == "__main__":
    arg_integration = sys.argv[1]
    arg_filename = sys.argv[2]

    main()
