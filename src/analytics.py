import re
import csv
from collections import defaultdict, Counter

class Analyzer:
    def __init__(self):
        self.search_pattern = re.compile(r'(\S+)\s.* for (\S+)')
        self.log_file = 'log_files/app_search_info.log'

    def log_processing(self, log = None):
        """
        Analyze the log to get search statistics
        :param log: .log file
        :return: defaultdict(Counter)
        """
        if not log:
            log = self.log_file
        data = defaultdict(Counter)
        with open(log, mode='rt') as log_file:
            for line in log_file:
                res = self.search_pattern.search(line)
                if res:
                    data[res.group(1)][res.group(2)] += 1
        return data

    def generate_csv(self, log = None):
        """
        Generate one CSV file for each date
        :param log: .log file
        :return: None
        """
        data = self.log_processing(log)
        for date in data:
            data_date = data[date]
            with open('{} search results.csv'.format(date), mode='wt') as csv_file:
                csv_writer = csv.writer(csv_file)
                for word, count in data_date.items():
                    csv_writer.writerow((word, count))
