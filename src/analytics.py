"""
    Main module for usage pattern analysis.
"""


import re
import csv
import os
from collections import defaultdict, Counter


class Analyzer:
    """
        Analyzer class for usage pattern analysis.

    """
    def __init__(self):
        self.search_pattern = re.compile(r'(\S+)\s.* for (\S+)')
        self.log_file = 'logs/app_search_info.log'

    def log_processing(self, log=None):
        """
        Analyze the log to get search statistics
        :param log: .log file
        :return: (defaultdict(Counter), Counter)
        """
        if not log:
            log = self.log_file
        data = defaultdict(Counter)
        overall_data = Counter()
        with open(log, mode='rt') as log_file:
            for line in log_file:
                res = self.search_pattern.search(line)
                if res:
                    date, word = res.group(1), res.group(2)
                    data[date][word] += 1
                    overall_data[word] += 1
        return data, overall_data

    def generate_csv(self, log=None, gen_csv_for_each_day=True):
        """
        Generate one CSV file for overall search history and optionally generate one CSV for each date
        :param log: .log file
        :param gen_csv_for_each_day: True if generate one CSV file for each date
        :return: None
        """
        data, overall_data = self.log_processing(log)

        if not os.path.exists("stats"):
            os.makedirs("stats")

        if gen_csv_for_each_day:
            for date in data:
                data_date = data[date]
                with open('stats/{} search results.csv'.format(date), mode='wt') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    for word, count in data_date.items():
                        csv_writer.writerow((word, count))

        with open('stats/up_to_date search results.csv', mode='wt') as file:
            csv_writer = csv.writer(file)
            for word, count in overall_data.items():
                csv_writer.writerow((word, count))


if __name__ == '__main__':
    analyzer = Analyzer()
    analyzer.generate_csv(log=None)
