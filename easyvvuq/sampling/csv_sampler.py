from .base import BaseSamplingElement
import json

__license__ = "LGPL"

class CSVSampler(BaseSamplingElement, sampler_name="csv_sampler"):

    def __init__(self, filename, counter=0):
        """
            Expects dict of var names, and their corresponding distributions
        """
        self.data = []
        self.filename = filename
        self.counter = counter
        try:
            with open(filename, 'r') as fd:
                reader = csv.DictReader(fd)
                for row in reader:
                    self.data.append(row)
        except FileNotFoundError:
            raise RuntimeError("CSV file you specified ({}) does not exist".format(filename))

    def element_version(self):
        return "0.1"

    def is_finite(self):
        return True

    def n_samples(self):
        """Returns the number of samples in this sampler.
        Returns
        -------
        if the user specifies maximum number of samples than return that, otherwise - error
        """
        return len(self.data)

    def __next__(self):
        try:
            return self.data[self.counter]
        finally:
            if self.counter < self.n_samples():
                self.counter += 1
            else:
                raise StopIteration

    def is_restartable(self):
        return True

    def get_restart_dict(self):
        return {"filename": self.filename, "counter": self.counter}
