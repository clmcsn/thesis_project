#!/usr/bin/env python3
import torch
from torch import tensor
import matplotlib
import matplotlib.pyplot as plt
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from scipy.stats import skewnorm

#cm = confusion matrix
#classes = classes that will be x and y axes
#

def plot_confusion_matrix(cm, classes, normalize=False, title='Confusion matrix', cmap=plt.cm.Blues):
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt), horizontalalignment="center", color="white" if cm[i, j] > thresh else "black")

    # plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.show(block=True)


def get_all_preds(model, loader, device="cpu"):
    all_preds = torch.tensor([]).to(device) #new pytorch sensor
    for batch in loader:
        images, labels = batch
        images = images.to(device)
        labels = labels.to(device)
        preds=model(images)
        all_preds = torch.cat(
            (all_preds, preds)
            ,dim=0)
    return all_preds

def train(log_interval, model, device, train_loader, optimizer, criterion, epoch):
    model.train()
    for batch_idx, (batch) in enumerate(train_loader):
        data, target = batch
        data = data.to(device)
        target = target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        correct = output.argmax(dim=1).eq(target).sum().item()
        accuracy = correct / len(target) 
        loss.backward()
        optimizer.step()
        quant_net.quantize_params()
        if batch_idx % log_interval == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}\tAccuracy: {}'.format(
                epoch, batch_idx * len(data), len(train_loader.dataset),
                100. * batch_idx / len(train_loader), loss.item(), accuracy))

def test(model, device, test_loader):
    model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            data = data.to(device)
            target = target.to(device)
            output = model(data)
            test_loss += F.nll_loss(output, target, reduction='sum').item()  # sum up batch loss
            pred = output.argmax(dim=1, keepdim=True)  # get the index of the max log-probability
            correct += pred.eq(target.view_as(pred)).sum().item()

    test_loss /= len(test_loader.dataset)

    print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
        test_loss, correct, len(test_loader.dataset),
        100. * correct / len(test_loader.dataset)))

def get_layersName_list(model):
    l=[]
    for name, module in model.named_modules():
        if isinstance(module, (nn.Conv2d, nn.Conv3d, nn.Linear)):
            l+=[name]
    return l

"""def print_weight_dist(layer,path,name='layer1',multiple=False,conf_layer=None,num_bins=50):
    x = torch.flatten(layer)
    x = x.detach().numpy() 
    fig, ax = plt.subplots()
    n, bins, patches = ax.hist(x, num_bins)
    if multiple:
        y = torch.flatten(conf_layer)
        y = y.detach().numpy()
        n2, bins2, patches2 = ax.hist(y, num_bins)
    ax.set_xlabel('Weight')
    ax.set_ylabel('Occurrency')
    ax.set_title(r'Histogram of {}: $\mu=100$, $\sigma=15$'.format(name))
    # Tweak spacing to prevent clipping of ylabel
    fig.tight_layout()  
    plt.savefig(path+name+".svg")"""#deprecated

def make_weightDistr_simpleHistogram(layer, name='layer', save=False, path=None):
    x = torch.flatten(layer)
    x = x.detach().numpy()
    fig, ax = plt.subplots()
    n, bins, patches = ax.hist(x, num_bins)
    ax.set_xlabel('Weight')
    ax.set_ylabel('Occurrency')
    ax.set_title('Histogram of {}'.format(name))
    fig.tight_layout()
    if save:
        plt.savefig(path+"/"+name+".svg")
    else:
        plt.show()

def make_weightDistr_comparHistgram(layer, reflayer, name='layer', save=False, path=None, num_bins=100):
    x = torch.flatten(layer)
    x = x.detach().numpy()
    y = torch.flatten(reflayer)
    y = y.detach().numpy()
    plt.hist(x, num_bins,facecolor='blue',label="unmasked")
    plt.hist(y, num_bins,facecolor='grey',label="masked")
    plt.legend(loc='upper right')
    plt.xlabel('Weight')
    plt.ylabel('Occurrencies')
    plt.title('Histogram of {}'.format(name))
    if save:
        plt.savefig(path+"/"+name+".svg")
    else:
        plt.show()
    plt.cla()
    plt.clf()
    plt.close()
    

#TODO to implement fitting curve
def make_weightDistr_skewfitHistogram(layer, name='layer', save=False, path=None):
    x = torch.flatten(layer)
    x = x.detach().numpy()
    fig, ax = plt.subplots()
    n, bins, patches = ax.hist(x, num_bins)
    ax.set_xlabel('Weight')
    ax.set_ylabel('Occurrencies')
    ax.set_title('Histogram of {}'.format(name))
    fig.tight_layout()
    if save:
        plt.savefig(path+"/"+name+".svg")
    else:
        plt.show()

class dumping_layer(nn.Module):

    def __init__(self,name):
        self.name = name
    
    def forward(self,x):
        with open("out_activation_dump_{}.dump".format(self.name),"w") as out_p:
            out_p.write(x)