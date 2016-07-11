"""
kmeans

Usage:
  kmeans fit [-p <params>] <data>
  kmeans predict <sample>

This is a quick description
"""
import pickle
import json
from io import StringIO
from time import time
from docopt import docopt
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import scale



def main():
    opts = docopt(__doc__)
    if opts['fit']:
        params_json = opts['<params>'] or "{}"
        params = json.loads(params_json)

        data_path = opts['<data>']

        data = pd.read_csv(data_path, index_col=0)

        my_model = KMeans(**params)

        X, y = scale(data.drop(['Species'], axis=1)), data['Species']

        n_samples, n_features = X.shape

        fitted_model = my_model.fit(X)

        pickle.dump(fitted_model, open("/opt/model/fitted.pkl", "wb"))

        print("n_species: %d, \t n_samples %d, \t n_features %d" % (4, n_samples, n_features))

    elif opts['predict']:

        fitted_model = pickle.load(open("/opt/model/fitted.pkl", "rb"))

        if opts['<sample>'] =="-":
            import sys
            in_sample = sys.stdin
        else:
            in_sample = StringIO(unicode(opts['<sample>']))

        sample = pd.read_csv(in_sample, header=None,
                             names=['id', 'feature', 'value'])

        sample = sample.pivot("id", "feature", "value")

        retval = fitted_model.predict(sample)

        rows = ((idx, "prediction", value) for idx, value in enumerate(retval))

        out = pd.DataFrame.from_records(
            rows, columns=['id', 'feature', 'value']
        ).to_csv(index=False, header=False)

        print(out)

    else:
        print(opts)


if __name__ == "__main__":
    main()

