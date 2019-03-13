import numpy as np
from collections import Counter
import torch
from torch.autograd import Variable

from matplotlib import gridspec
import matplotlib.pyplot as plt

from ._train_utils import predict_labels


def show_samples_of_classes_and_reconstructions(Q, P, valid_loader, n_classes=10, z_dim=2):
    batch_size = valid_loader.batch_size
    labels = []

    for _, (X, y) in enumerate(valid_loader):

        X.resize_(batch_size, Q.input_size)

        X, y = Variable(X), Variable(y)
        if cuda:
            X, y = X.cuda(), y.cuda()

        show_sample_from_each_class(Q, P, X, n_classes=n_classes, z_dim=z_dim)
        plt.show()

        show_reconstruction(Q, P, X)
        plt.show()


def show_reconstruction(Q, P, X):
    Q.eval()
    P.eval()

    latent_y, latent_z = Q(X)

    latent_vec = torch.cat((latent_y, latent_z), 1)
    X_rec = P(latent_vec)

    img_orig = np.array(X[0].data.tolist()).reshape(28, 28)
    img_rec = np.array(X_rec[0].data.tolist()).reshape(28, 28)
    plt.subplot(1, 2, 1)
    plt.imshow(img_orig, cmap='gray')
    plt.subplot(1, 2, 2)
    plt.imshow(img_rec, cmap='gray')
    plt.title('predicted label: %s' % torch.argmax(latent_y, dim=1)[0])


def show_sample_from_each_class(Q, P, X, n_classes, z_dim):

    Q.eval()

    latent_y, latent_z = Q(X)
    y_class = torch.argmax(latent_y, dim=1).numpy()

    fig, ax = plt.subplots(nrows=n_classes, ncols=9)

    X_samples = {}
    for label in range(n_classes):
        label_indices = np.where(y_class == label)
        try:
            X_samples[label] = X[label_indices][:8, :]  # take first 8   images
        except:
            X_samples[label] = None

    for label in range(n_classes):
        latent_y = np.eye(n_classes)[label].astype('float32')
        latent_y = torch.from_numpy(latent_y)
        latent_y = Variable(latent_y).reshape(1, n_classes)

        latent_z = Variable(torch.zeros(1, z_dim))


    for i, row in zip(range(n_classes), ax):
        for j, col in zip(range(9), row):
            if j == 0:  # first column shows the "mode" of the labels generated by the latent space
                latent_y = np.eye(n_classes)[i].astype('float32')
                latent_y = torch.from_numpy(latent_y)
                latent_y = Variable(latent_y).reshape(1, n_classes)

                latent_z = Variable(torch.zeros(1, z_dim))

                latent_vec = torch.cat((latent_y, latent_z), 1)
                X_mode_rec = P(latent_vec)

                mode_img = np.array(X_mode_rec.data.tolist()).reshape(28, 28)
                col.axis('off')
                col.imshow(mode_img, cmap='gray')

            else:  # show actual images predicted to be part of the current label
                col.axis('off')
                try:
                    img = X_samples[i][j]
                    img = np.array(img.data.tolist()).reshape(28, 28)
                    col.imshow(img, cmap='gray')
                except:
                    col.imshow(np.zeros((28, 28)), cmap='gray')

    plt.suptitle('Representative mode & samples from each possible label')
    fig.show()


def plot_latent_distribution(P, valid_loader):
    batch_size = valid_loader.batch_size
    labels = []

    _, (X, y) = enumerate(valid_loader).next()  # take first batch
    X.resize_(batch_size, Q.input_size)

    X, y = Variable(X), Variable(y)
    if cuda:
        X, y = X.cuda(), y.cuda()

    latent_y, latent_z = Q(X)

    y_highest_prob = []
    for latent_y_vec in latent_y:
        sorted_p = latent_y_vec.sort(descending=True)[0].detach().numpy()
        y_highest_prob.append(sorted_p[0])

    plt.figure()
    plt.hist(y_highest_prob, bins=15)
    plt.title('distribution of highest "probability" given by the latent y vector')
    plt.show()

    plt.figure()
    plt.hist(latent_z.detach().numpy()[:, 0])
    plt.title('distribution of the first element of the latent z vector')
    plt.show()


def plot_predicted_label_distribution(P, valid_loader, n_classes=10):
    batch_size = valid_loader.batch_size
    labels = []

    for _, (X, y) in enumerate(valid_loader):

        X.resize_(batch_size, Q.input_size)

        X, y = Variable(X), Variable(y)
        if cuda:
            X, y = X.cuda(), y.cuda()

        y_pred = predict_labels(Q, X)
        latent_y, latent_z = Q(X)

        labels.extend(y_pred.numpy())

    plt.figure()
    plt.title('distribution of the predicted labels')
    plt.hist(labels, bins=n_classes)
    plt.show()

    return Counter(labels)


def show_learned_latent_features(P, n_classes=10, z_dim=2):

    subplot_ind = 1

    for label in range(n_classes):
        latent_y = np.eye(n_classes)[label].astype('float32')
        latent_y = torch.from_numpy(latent_y)
        latent_y = Variable(latent_y).reshape(1, n_classes)

        for j, z0 in zip(range(10), torch.linspace(-1, 1, 10)):
            latent_z = Variable(torch.zeros(1, z_dim))
            # scan over z0 values in-order
            latent_z[0, 0] = z0

            latent_vec = torch.cat((latent_y, latent_z), 1)
            X_mode_rec = P(latent_vec)

            mode_img = np.array(X_mode_rec.data.tolist()).reshape(28, 28)
            plt.subplot(n_classes, 10, subplot_ind)
            plt.imshow(mode_img, cmap='gray')
            plt.axis('off')
            subplot_ind += 1

    plt.suptitle('latent feature impact of decoded image')
    plt.show()

def show_all_learned_modes(P_mode_decoder, n_classes=10):

    for label in range(n_classes):
        latent_y = np.eye(n_classes)[label].astype('float32')
        latent_y = torch.from_numpy(latent_y)
        latent_y = Variable(latent_y)

        X_mode_rec = P_mode_decoder(latent_y)
        mode_img = np.array(X_mode_rec.data.tolist()).reshape(28, 28)
        plt.subplot(1, n_classes, label + 1)
        plt.imshow(mode_img, cmap='gray')
        plt.title(label)
        plt.axis('off')

    plt.suptitle('learned modes')
    plt.show()


def generate_digits(P, label, n_classes=10, z_dim=2):
    P.eval()

    latent_y = np.eye(n_classes)[label].astype('float32')
    latent_y = Variable(torch.from_numpy(latent_y).resize_(1, n_classes))

    while True:
        latent_z = Variable(torch.randn(1, z_dim))
        latent_vec = torch.cat((latent_y, latent_z), 1)

        X_rec = P(latent_vec)
        plt.imshow(np.array(X_rec[0].data.tolist()).reshape(28, 28), cmap='gray')
        plt.show()


def unsupervised_accuracy_score(Q, valid_loader, n_classes=10):
    batch_size = valid_loader.batch_size
    labels = []

    true_to_pred = {}
    pred_to_true = {}

    for _, (X, y) in enumerate(valid_loader):

        X.resize_(batch_size, Q.input_size)

        X, y = Variable(X), Variable(y)
        if cuda:
            X, y = X.cuda(), y.cuda()

        y_pred = predict_labels(Q, X)

        for y_true, y_hat in zip(y, y_pred):
            true_to_pred.setdefault(y_true.item(), {})
            true_to_pred[y_true.item()].setdefault(y_hat.item(), 0)
            true_to_pred[y_true.item()][y_hat.item()] += 1

            pred_to_true.setdefault(y_hat.item(), {})
            pred_to_true[y_hat.item()].setdefault(y_true.item(), 0)
            pred_to_true[y_hat.item()][y_true.item()] += 1

    for y_true in range(10):  # true classes are always 0-10
        n_samples = sum(true_to_pred[y_true].values())
        best_match_label = max(true_to_pred[y_true], key=true_to_pred[y_true].get)
        n_highest_match = true_to_pred[y_true][best_match_label]
        print("Label {}: {}%, Best matching label; {}".format(y_true, 100.0 * n_highest_match / n_samples, best_match_label))


    correct = 0
    wrong = 0
    label_mapping = {}
    for y_hat in range(n_classes):
        try:
            label_mapping[y_hat] = max(pred_to_true[y_hat], key=pred_to_true[y_hat].get)
            correct += pred_to_true[y_hat][label_mapping[y_hat]]
            wrong += sum([v for  k, v in pred_to_true[y_hat].iteritems() if k != label_mapping[y_hat]])
        except:
            print("label %s in never predicted" % y_hat)

    print("ACCURACY: %.2f%%" % (float(correct) / (wrong + correct)))

    print(label_mapping)
    print(pred_to_true)
    return true_to_pred


import os
from _model import Q_net, P_net

mode = 'unsupervised'
data_dir = '../data'
#data_dir = '../data/2.3 10:40AM'
n_classes = 16
z_dim = 2

Q = Q_net().load(os.path.join(data_dir, 'encoder_{}'.format(mode)), z_size=z_dim, n_classes=n_classes)
P = P_net().load(os.path.join(data_dir, 'decoder_{}'.format(mode)), z_size=z_dim, n_classes=n_classes)
P_mode_decoder = P_net().load(os.path.join(data_dir, 'mode_decoder_unsupervised'), z_size=0, n_classes=n_classes)

import _data_utils
cuda = torch.cuda.is_available()
kwargs = {'num_workers': 1, 'pin_memory': True} if cuda else {}
train_labeled_loader, train_unlabeled_loader, valid_loader = _data_utils.load_data(
    data_path='../data', batch_size=100, **kwargs)

plot_latent_distribution(P, valid_loader)
print(plot_predicted_label_distribution(P, valid_loader, n_classes=n_classes))
print(unsupervised_accuracy_score(Q, valid_loader, n_classes=n_classes))
show_learned_latent_features(P, n_classes=n_classes, z_dim=z_dim)
show_all_learned_modes(P_mode_decoder, n_classes=n_classes)
show_samples_of_classes_and_reconstructions(Q, P, valid_loader, n_classes=n_classes, z_dim=z_dim)
