from lasagne import layers
from lasagne.nonlinearities import rectify, softmax
from lasagne.updates import nesterov_momentum
from nolearn.lasagne import NeuralNet
from nolearn.lasagne import PrintLayerInfo
from nolearn.lasagne import TrainSplit
import cPickle as pickle
import pandas as pd
import numpy as np


class MyTrainSplit(TrainSplit):
    """Class to modify nolearn's train split so that each class has the
    same amount in the train and test.
    """
    def __call__(self, X, y, net):
        train_index = []
        test_index = []
        for val in np.unique(y):
            indexes = np.where(y == val)[0]
            length = len(indexes)
            train_index.extend(indexes[int(length * self.eval_size):])
            test_index.extend(indexes[:int(length * self.eval_size)])
        return X[train_index], X[test_index], y[train_index], y[test_index]


class SaveBestModel(object):
    """Class to save the model if the validation accuracy improves."""
    def __init__(self, name):
        self.best = 0.
        self.name = name.split('.')[0]

    def __call__(self, nn, train_history):
        score = train_history[-1]['valid_accuracy']
        if score > self.best:
            self.best = score
            nn.save_params_to(self.name + '.pkl')
        nn.save_params_to(self.name + '_last.pkl')


def build_model(num_labels):
    """Builds a nolearn neural net. Also used to load a pickled model."""
    filter_size1 = 50
    filter_size2 = 100
    mdl = NeuralNet(
        layers=[('input', layers.InputLayer),
                ('conv1', layers.Conv2DLayer),
                ('pool1', layers.Pool2DLayer),
                ('conv2', layers.Conv2DLayer),
                ('pool2', layers.Pool2DLayer),
                ('hidden1', layers.DenseLayer),
                ('hidden2', layers.DenseLayer),
                ('output', layers.DenseLayer)],

        # input
        input_shape=(None, 1, 28, 28),

        # conv1
        conv1_num_filters=filter_size1,
        conv1_filter_size=(3, 3),
        conv1_nonlinearity=rectify,
        conv1_pad=1,

        # pool1
        pool1_pool_size=(2, 2),
        pool1_mode='max',

        # conv2
        conv2_num_filters=filter_size2,
        conv2_filter_size=(3, 3),
        conv2_nonlinearity=rectify,
        conv2_pad=1,

        # pool2
        pool2_pool_size=(2, 2),
        pool2_mode='max',

        # hidden1
        hidden1_num_units=1000,
        hidden1_nonlinearity=rectify,

        # hidden2
        hidden2_num_units=200,
        hidden2_nonlinearity=rectify,

        # output
        output_num_units=num_labels,
        output_nonlinearity=softmax,

        # Optimization
        update=nesterov_momentum,
        update_learning_rate=0.007,
        update_momentum=0.6,
        max_epochs=200,

        # Save best model
        on_epoch_finished=[SaveBestModel('cnn_handle_frac.pkl')],

        # My train split
        train_split=MyTrainSplit(eval_size=0.2),

        regression=False,
        verbose=2
    )

    return mdl


def main():
    df = pd.read_json('compiled.json')
    X = df['img']
    X = list(X.map(lambda x: list(np.array(x, np.float32) / 255)).values)
    X = np.array(X, dtype=np.float32)
    X = X.reshape(X.shape[0], 1, X.shape[1], X.shape[2])
    y = df['encode'].values.astype(np.int32)

    num_labels = len(np.unique(y))
    mdl = build_model(num_labels)

    # layer_info = PrintLayerInfo()
    # mdl.initialize()
    # layer_info(mdl)

    mdl.fit(X, y)


if __name__ == '__main__':
    main()
