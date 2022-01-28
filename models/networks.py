"""
ResNet code gently borrowed from
https://github.com/pytorch/vision/blob/master/torchvision/models/resnet.py
"""
from __future__ import print_function, division, absolute_import

import math
import os
from collections import OrderedDict

import torch
import torch.nn as nn
from torch.utils import model_zoo

__all__ = ['SENet', 'senet154', 'se_resnet50', 'se_resnet101', 'se_resnet152',
           'se_resnext50_32x4d', 'se_resnext40_32x4d', 'se_resnext101_32x4d', 'output_maxpool', 'make_network']


def make_network(name, pretrained='imagenet', n_cls=1000, input_3x3=False, n_channels=1):
    torch.hub.set_dir(os.path.join(os.environ['PWD'], "pretrained"))
    if name == 'senet154':
        net = senet154(n_cls, pretrained, input_3x3=input_3x3)
    elif name == 'se_resnet50':
        net = se_resnet50(n_cls, pretrained, input_3x3=input_3x3)
    elif name == 'se_resnet101':
        net = se_resnet101(n_cls, pretrained, input_3x3=input_3x3)
    elif name == 'se_resnet152':
        net = se_resnet152(n_cls, pretrained, input_3x3=input_3x3)
    elif name == 'se_resnext50_32x4d':
        net = se_resnext50_32x4d(n_cls, pretrained, input_3x3=input_3x3)
    elif name == 'se_resnext40_32x4d':
        net = se_resnext40_32x4d(n_cls, pretrained, input_3x3=input_3x3)
    elif name == 'se_resnext101_32x4d':
        net = se_resnext101_32x4d(n_cls, pretrained, input_3x3=input_3x3)
    elif name == 'custom_resnet':
        net = CustomResnet(n_classes=n_cls, in_channels=n_channels, n_features=64, drop_rate=0.2)
    elif name == 'resnet18':
        net = torch.hub.load('pytorch/vision:v0.6.0', 'resnet18', pretrained=True)
        if input_3x3:
            net.conv1 = nn.Sequential(
            nn.Conv2d(n_channels, 64, 3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, 3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, 3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True))
        else:
            net.conv1 = nn.Conv2d(n_channels, 64, 7, 2, 3, bias=False)
    elif name == 'minivgg':
        net = MiniVGG(in_channels=1)
    else:
        raise ValueError(f'Not support network name {name}')
    return net


pretrained_settings = {
    'senet154': {
        'imagenet': {
            'url': 'http://data.lip6.fr/cadene/pretrainedmodels/senet154-c7b49a05.pth',
            'input_space': 'RGB',
            'input_size': [3, 224, 224],
            'input_range': [0, 1],
            'mean': [0.485, 0.456, 0.406],
            'std': [0.229, 0.224, 0.225],
            'num_classes': 1000
        }
    },
    'se_resnet50': {
        'imagenet': {
            'url': 'http://data.lip6.fr/cadene/pretrainedmodels/se_resnet50-ce0d4300.pth',
            'input_space': 'RGB',
            'input_size': [3, 224, 224],
            'input_range': [0, 1],
            'mean': [0.485, 0.456, 0.406],
            'std': [0.229, 0.224, 0.225],
            'num_classes': 1000
        }
    },
    'se_resnet101': {
        'imagenet': {
            'url': 'http://data.lip6.fr/cadene/pretrainedmodels/se_resnet101-7e38fcc6.pth',
            'input_space': 'RGB',
            'input_size': [3, 224, 224],
            'input_range': [0, 1],
            'mean': [0.485, 0.456, 0.406],
            'std': [0.229, 0.224, 0.225],
            'num_classes': 1000
        }
    },
    'se_resnet152': {
        'imagenet': {
            'url': 'http://data.lip6.fr/cadene/pretrainedmodels/se_resnet152-d17c99b7.pth',
            'input_space': 'RGB',
            'input_size': [3, 224, 224],
            'input_range': [0, 1],
            'mean': [0.485, 0.456, 0.406],
            'std': [0.229, 0.224, 0.225],
            'num_classes': 1000
        }
    },
    'se_resnext50_32x4d': {
        'imagenet': {
            'url': 'http://data.lip6.fr/cadene/pretrainedmodels/se_resnext50_32x4d-a260b3a4.pth',
            'input_space': 'RGB',
            'input_size': [3, 224, 224],
            'input_range': [0, 1],
            'mean': [0.485, 0.456, 0.406],
            'std': [0.229, 0.224, 0.225],
            'num_classes': 1000
        }
    },
    'se_resnext40_32x4d': {
        'imagenet': {
            'url': 'http://data.lip6.fr/cadene/pretrainedmodels/se_resnext50_32x4d-a260b3a4.pth',
            'input_space': 'RGB',
            'input_size': [3, 224, 224],
            'input_range': [0, 1],
            'mean': [0.485, 0.456, 0.406],
            'std': [0.229, 0.224, 0.225],
            'num_classes': 1000
        }
    },
    'se_resnext101_32x4d': {
        'imagenet': {
            'url': 'http://data.lip6.fr/cadene/pretrainedmodels/se_resnext101_32x4d-3b2fe3d8.pth',
            'input_space': 'RGB',
            'input_size': [3, 224, 224],
            'input_range': [0, 1],
            'mean': [0.485, 0.456, 0.406],
            'std': [0.229, 0.224, 0.225],
            'num_classes': 1000
        }
    },
}


class MiniVGG(nn.Module):
    def __init__(self, in_channels, drop_rate=0.2):
        super().__init__()
        self.dropout = nn.Dropout(drop_rate)
        self.layer0 = nn.Sequential(
            nn.Conv2d(in_channels, 16, 3, 1, 1, bias=False),
            nn.ReLU(),
            nn.Conv2d(16, 16, 3, 1, 1, bias=False),
            nn.ReLU()
        )

        self.layer1 = nn.Sequential(
            nn.Conv2d(16, 32, 3, 2, 1, bias=False),
            nn.ReLU()
        )
        self.layer2 = nn.Sequential(
            nn.Conv2d(32, 64, 3, 2, 1, bias=False),
            nn.ReLU()
        )

    def forward(self, x):
        x = self.layer0(x)
        x = self.layer1(x)
        x = self.layer2(x)
        return x


class ResBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride):
        super().__init__()
        if in_channels != out_channels or stride != 1:
            self.bn1 = nn.BatchNorm2d(in_channels)
            self.relu1 = nn.ReLU()
            self.conv1 = nn.Conv2d(in_channels, out_channels, 1, stride, 0, bias=False)

            self.branch1 = nn.Sequential(self.bn1, self.relu1, self.conv1)

        else:
            self.branch1 = nn.Sequential(nn.BatchNorm2d(in_channels), nn.ReLU())

        self.conv2 = nn.Conv2d(in_channels, out_channels, 3, stride, 1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        self.relu2 = nn.ReLU()
        self.conv3 = nn.Conv2d(out_channels, out_channels, 3, 1, 1, bias=False)

        self.branch2 = nn.Sequential(self.conv2, self.bn2, self.relu2, self.conv3)

    def forward(self, x):
        x1 = self.branch1(x)
        x2 = self.branch2(x)
        return x1 + x2


class CustomResnet(nn.Module):
    def __init__(self, in_channels=3, n_features=64, drop_rate=0.2, n_classes=10):
        super().__init__()
        c = [n_features, 2 * n_features, 4 * n_features, 4 * n_features]
        self.layer0 = nn.Conv2d(in_channels, n_features, kernel_size=3, stride=1, padding=1, bias=False)

        self.layer1 = nn.Sequential(ResBlock(c[0], c[0], 1),
                                    ResBlock(c[0], c[0], 1))

        self.layer2 = nn.Sequential(ResBlock(c[0], c[1], 2),
                                    ResBlock(c[1], c[1], 1))

        self.layer3 = nn.Sequential(ResBlock(c[1], c[2], 2),
                                    ResBlock(c[2], c[2], 1))

        self.layer4 = nn.Sequential(ResBlock(c[2], c[3], 2),
                                    ResBlock(c[3], c[3], 1))

        self.drop = nn.Dropout(drop_rate)

        self.avgpool = nn.AvgPool2d(4)

        self.linear = nn.Linear(c[3], n_classes, bias=True)

    def forward(self, x):
        o = self.prep(x)
        o = self.layer1(o)
        o = self.drop(o)
        o = self.layer2(o)
        o = self.drop(o)
        o = self.layer3(o)
        o = self.drop(o)
        o = self.layer4(o)
        o = self.avgpool(o).view(o.shape[0], -1)
        o = self.drop(o)
        out = self.linear(o)

        return out


class SEModule(nn.Module):

    def __init__(self, channels, reduction):
        super(SEModule, self).__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.fc1 = nn.Conv2d(channels, channels // reduction, kernel_size=1,
                             padding=0)
        self.relu = nn.ReLU(inplace=True)
        self.fc2 = nn.Conv2d(channels // reduction, channels, kernel_size=1,
                             padding=0)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        module_input = x
        x = self.avg_pool(x)
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        x = self.sigmoid(x)
        return module_input * x


class Bottleneck(nn.Module):
    """
    Base class for bottlenecks that implements `forward()` method.
    """

    def forward(self, x):
        residual = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)
        out = self.relu(out)

        out = self.conv3(out)
        out = self.bn3(out)

        if self.downsample is not None:
            residual = self.downsample(x)

        out = self.se_module(out) + residual
        out = self.relu(out)

        return out


class SEBottleneck(Bottleneck):
    """
    Bottleneck for SENet154.
    """
    expansion = 4

    def __init__(self, inplanes, planes, groups, reduction, stride=1,
                 downsample=None):
        super(SEBottleneck, self).__init__()
        self.conv1 = nn.Conv2d(inplanes, planes * 2, kernel_size=1, bias=False)
        self.bn1 = nn.BatchNorm2d(planes * 2)
        self.conv2 = nn.Conv2d(planes * 2, planes * 4, kernel_size=3,
                               stride=stride, padding=1, groups=groups,
                               bias=False)
        self.bn2 = nn.BatchNorm2d(planes * 4)
        self.conv3 = nn.Conv2d(planes * 4, planes * 4, kernel_size=1,
                               bias=False)
        self.bn3 = nn.BatchNorm2d(planes * 4)
        self.relu = nn.ReLU(inplace=True)
        self.se_module = SEModule(planes * 4, reduction=reduction)
        self.downsample = downsample
        self.stride = stride


class SEResNetBottleneck(Bottleneck):
    """
    ResNet bottleneck with a Squeeze-and-Excitation module. It follows Caffe
    implementation and uses `stride=stride` in `conv1` and not in `conv2`
    (the latter is used in the torchvision implementation of ResNet).
    """
    expansion = 4

    def __init__(self, inplanes, planes, groups, reduction, stride=1,
                 downsample=None):
        super(SEResNetBottleneck, self).__init__()
        self.conv1 = nn.Conv2d(inplanes, planes, kernel_size=1, bias=False,
                               stride=stride)
        self.bn1 = nn.BatchNorm2d(planes)
        self.conv2 = nn.Conv2d(planes, planes, kernel_size=3, padding=1,
                               groups=groups, bias=False)
        self.bn2 = nn.BatchNorm2d(planes)
        self.conv3 = nn.Conv2d(planes, planes * 4, kernel_size=1, bias=False)
        self.bn3 = nn.BatchNorm2d(planes * 4)
        self.relu = nn.ReLU(inplace=True)
        self.se_module = SEModule(planes * 4, reduction=reduction)
        self.downsample = downsample
        self.stride = stride


class SEResNeXtBottleneck(Bottleneck):
    """
    ResNeXt bottleneck type C with a Squeeze-and-Excitation module.
    """
    expansion = 4

    def __init__(self, inplanes, planes, groups, reduction, stride=1,
                 downsample=None, base_width=4):
        super(SEResNeXtBottleneck, self).__init__()
        width = math.floor(planes * (base_width / 64)) * groups
        self.conv1 = nn.Conv2d(inplanes, width, kernel_size=1, bias=False,
                               stride=1)
        self.bn1 = nn.BatchNorm2d(width)
        self.conv2 = nn.Conv2d(width, width, kernel_size=3, stride=stride,
                               padding=1, groups=groups, bias=False)
        self.bn2 = nn.BatchNorm2d(width)
        self.conv3 = nn.Conv2d(width, planes * 4, kernel_size=1, bias=False)
        self.bn3 = nn.BatchNorm2d(planes * 4)
        self.relu = nn.ReLU(inplace=True)
        self.se_module = SEModule(planes * 4, reduction=reduction)
        self.downsample = downsample
        self.stride = stride


def output_maxpool(input_shape, padding=0, dilation=0, ks=2, stride=2):
    return math.floor((input_shape + 2 * padding - dilation * (ks - 1) - 1) / 2 + 1)


class SENet(nn.Module):

    def __init__(self, block, layers, groups, reduction, input_shape, dropout_p=0.2,
                 inplanes=128, input_3x3=True, downsample_kernel_size=3,
                 downsample_padding=1, num_classes=1000, order='conv-relu-norm'):
        """
        Parameters
        ----------
        block (nn.Module): Bottleneck class.
            - For SENet154: SEBottleneck
            - For SE-ResNet models: SEResNetBottleneck
            - For SE-ResNeXt models:  SEResNeXtBottleneck
        layers (list of ints): Number of residual blocks for 4 layers of the
            network (layer1...layer4).
        groups (int): Number of groups for the 3x3 convolution in each
            bottleneck block.
            - For SENet154: 64
            - For SE-ResNet models: 1
            - For SE-ResNeXt models:  32
        reduction (int): Reduction ratio for Squeeze-and-Excitation modules.
            - For all models: 16
        dropout_p (float or None): Drop probability for the Dropout layer.
            If `None` the Dropout layer is not used.
            - For SENet154: 0.2
            - For SE-ResNet models: None
            - For SE-ResNeXt models: None
        inplanes (int):  Number of input channels for layer1.
            - For SENet154: 128
            - For SE-ResNet models: 64
            - For SE-ResNeXt models: 64
        input_3x3 (bool): If `True`, use three 3x3 convolutions instead of
            a single 7x7 convolution in layer0.
            - For SENet154: True
            - For SE-ResNet models: False
            - For SE-ResNeXt models: False
        downsample_kernel_size (int): Kernel size for downsampling convolutions
            in layer2, layer3 and layer4.
            - For SENet154: 3
            - For SE-ResNet models: 1
            - For SE-ResNeXt models: 1
        downsample_padding (int): Padding for downsampling convolutions in
            layer2, layer3 and layer4.
            - For SENet154: 1
            - For SE-ResNet models: 0
            - For SE-ResNeXt models: 0
        num_classes (int): Number of outputs in `last_linear` layer.
            - For all models: 1000
        """
        super(SENet, self).__init__()
        # print('SENet')
        self.input_shape = input_shape
        self.inplanes = inplanes
        self.order = order
        self.default_order = 'conv-relu-norm'
        if input_3x3:
            if self.order == self.default_order:
                layer0_modules = [
                    # ('conv11', nn.Conv2d(3, 64, 3, stride=2, padding=1,
                    #                     bias=False)),
                    ('conv11_c1', nn.Conv2d(1, 64, 3, stride=2, padding=1,
                                            bias=False)),
                    ('bn11', nn.BatchNorm2d(64)),
                    ('relu11', nn.ReLU(inplace=True)),
                    ('conv12', nn.Conv2d(64, 64, 3, stride=1, padding=1,
                                         bias=False)),
                    ('bn12', nn.BatchNorm2d(64)),
                    ('relu12', nn.ReLU(inplace=True)),
                    ('conv13', nn.Conv2d(64, inplanes, 3, stride=1, padding=1,
                                         bias=False)),
                    ('bn13', nn.BatchNorm2d(inplanes)),
                    ('relu13', nn.ReLU(inplace=True)),
                ]
            else:
                layer0_modules = [
                    # ('conv11', nn.Conv2d(3, 64, 3, stride=2, padding=1,
                    #                     bias=False)),
                    ('conv11_c1', nn.Conv2d(1, 64, 3, stride=2, padding=1,
                                            bias=False)),
                    ('bn12', nn.BatchNorm2d(64)),
                    ('relu12', nn.ReLU(inplace=True)),
                    ('conv12', nn.Conv2d(64, 64, 3, stride=1, padding=1,
                                         bias=False)),
                    ('bn13', nn.BatchNorm2d(inplanes)),
                    ('relu13', nn.ReLU(inplace=True)),
                    ('conv13', nn.Conv2d(64, inplanes, 3, stride=1, padding=1,
                                         bias=False)),
                ]
        else:
            if self.order == self.default_order:
                layer0_modules = [
                    # ('conv1', nn.Conv2d(3, inplanes, kernel_size=7, stride=2,
                    #                     padding=3, bias=False)),
                    ('conv1_c1', nn.Conv2d(1, inplanes, kernel_size=7, stride=2,
                                           padding=3, bias=False)),
                    ('bn1', nn.BatchNorm2d(inplanes)),
                    ('relu1', nn.ReLU(inplace=True)),
                ]
            else:
                layer0_modules = [
                    # ('conv1', nn.Conv2d(3, inplanes, kernel_size=7, stride=2,
                    #                     padding=3, bias=False)),
                    ('conv1_c1', nn.Conv2d(1, inplanes, kernel_size=7, stride=2,
                                           padding=3, bias=False)),
                ]
        # To preserve compatibility with Caffe weights `ceil_mode=True`
        # is used instead of `padding=1`.
        layer0_modules.append(('pool', nn.MaxPool2d(3, stride=2,
                                                    ceil_mode=True)))
        self.layer0 = nn.Sequential(OrderedDict(layer0_modules))
        self.layer1 = self._make_layer(
            block,
            planes=64,
            blocks=layers[0],
            groups=groups,
            reduction=reduction,
            downsample_kernel_size=1,
            downsample_padding=0
        )
        self.layer2 = self._make_layer(
            block,
            planes=128,
            blocks=layers[1],
            stride=2,
            groups=groups,
            reduction=reduction,
            downsample_kernel_size=downsample_kernel_size,
            downsample_padding=downsample_padding
        )
        self.layer3 = self._make_layer(
            block,
            planes=256,
            blocks=layers[2],
            stride=2,
            groups=groups,
            reduction=reduction,
            downsample_kernel_size=downsample_kernel_size,
            downsample_padding=downsample_padding
        )
        self.layer4 = self._make_layer(
            block,
            planes=512,
            blocks=layers[3],
            stride=2,
            groups=groups,
            reduction=reduction,
            downsample_kernel_size=downsample_kernel_size,
            downsample_padding=downsample_padding
        )

    def _make_layer(self, block, planes, blocks, groups, reduction, stride=1,
                    downsample_kernel_size=1, downsample_padding=0, order='conv-relu-norm'):
        downsample = None
        if stride != 1 or self.inplanes != planes * block.expansion:
            downsample = nn.Sequential(
                nn.Conv2d(self.inplanes, planes * block.expansion,
                          kernel_size=downsample_kernel_size, stride=stride,
                          padding=downsample_padding, bias=False),
                nn.BatchNorm2d(planes * block.expansion),
            )

        layers = []
        layers.append(block(self.inplanes, planes, groups, reduction, stride,
                            downsample))
        self.inplanes = planes * block.expansion
        for i in range(1, blocks):
            layers.append(block(self.inplanes, planes, groups, reduction))

        return nn.Sequential(*layers)

    def features(self, x):
        x = self.layer0(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        return x

    # def logits(self, x):
    #     x = self.avg_pool(x)
    #     if self.dropout is not None:
    #         x = self.dropout(x)
    #     x = x.view(x.size(0), -1)
    #     x = self.last_linear(x)
    #     return x

    def forward(self, x):
        x = self.features(x)
        return x


def initialize_pretrained_model(model, num_classes, settings):
    assert num_classes == settings['num_classes'], \
        'num_classes should be {}, but is {}'.format(
            settings['num_classes'], num_classes)
    model.load_state_dict(model_zoo.load_url(settings['url']), strict=False)
    model.input_space = settings['input_space']
    model.input_size = settings['input_size']
    model.input_range = settings['input_range']
    model.mean = settings['mean']
    model.std = settings['std']


def senet154(num_classes=1000, pretrained='imagenet', input_3x3=True):
    model = SENet(SEBottleneck, [3, 8, 36, 3], groups=64, reduction=16, input_shape=300,
                  dropout_p=0.2, num_classes=num_classes)
    if pretrained is not None:
        settings = pretrained_settings['senet154'][pretrained]
        initialize_pretrained_model(model, num_classes, settings)
    return model


def se_resnet50(num_classes=1000, pretrained='imagenet', input_3x3=True):
    print('se_resnet50')
    model = SENet(SEResNetBottleneck, [3, 4, 6, 3], groups=1, reduction=16,
                  dropout_p=None, inplanes=64, input_3x3=input_3x3, input_shape=300,
                  downsample_kernel_size=1, downsample_padding=0,
                  num_classes=num_classes)
    if pretrained is not None:
        settings = pretrained_settings['se_resnet50'][pretrained]
        initialize_pretrained_model(model, num_classes, settings)
    return model


def se_resnet101(num_classes=1000, pretrained='imagenet', input_3x3=True):
    model = SENet(SEResNetBottleneck, [3, 4, 23, 3], groups=1, reduction=16,
                  dropout_p=None, inplanes=64, input_3x3=input_3x3, input_shape=300,
                  downsample_kernel_size=1, downsample_padding=0,
                  num_classes=num_classes)
    if pretrained is not None:
        settings = pretrained_settings['se_resnet101'][pretrained]
        initialize_pretrained_model(model, num_classes, settings)
    return model


def se_resnet152(num_classes=1000, pretrained='imagenet', input_3x3=True):
    model = SENet(SEResNetBottleneck, [3, 8, 36, 3], groups=1, reduction=16,
                  dropout_p=None, inplanes=64, input_3x3=input_3x3, input_shape=300,
                  downsample_kernel_size=1, downsample_padding=0,
                  num_classes=num_classes)
    if pretrained is not None:
        settings = pretrained_settings['se_resnet152'][pretrained]
        initialize_pretrained_model(model, num_classes, settings)
    return model


def se_resnext50_32x4d(num_classes=1000, pretrained='imagenet', input_3x3=True):
    model = SENet(SEResNeXtBottleneck, [3, 4, 6, 3], groups=32, reduction=16,
                  dropout_p=None, inplanes=64, input_3x3=input_3x3, input_shape=300,
                  downsample_kernel_size=1, downsample_padding=0,
                  num_classes=num_classes)
    if pretrained is not None:
        settings = pretrained_settings['se_resnext50_32x4d'][pretrained]
        initialize_pretrained_model(model, num_classes, settings)
    return model


def se_resnext40_32x4d(num_classes=1000, pretrained='imagenet', input_3x3=True):
    pretrained = None
    model = SENet(SEResNeXtBottleneck, [4, 5, 3, 2], groups=32, reduction=16,
                  dropout_p=None, inplanes=64, input_3x3=input_3x3, input_shape=300,
                  downsample_kernel_size=1, downsample_padding=0,
                  num_classes=num_classes)
    if pretrained is not None:
        settings = pretrained_settings['se_resnext50_32x4d'][pretrained]
        initialize_pretrained_model(model, num_classes, settings)
    return model


def se_resnext101_32x4d(num_classes=1000, pretrained='imagenet', input_3x3=True):
    model = SENet(SEResNeXtBottleneck, [3, 4, 23, 3], groups=32, reduction=16,
                  dropout_p=None, inplanes=64, input_3x3=input_3x3, input_shape=300,
                  downsample_kernel_size=1, downsample_padding=0,
                  num_classes=num_classes)
    if pretrained is not None:
        settings = pretrained_settings['se_resnext101_32x4d'][pretrained]
        initialize_pretrained_model(model, num_classes, settings)
    return model


def get_output_channels(seq, n_blocks):
    if n_blocks > 1:
        last_seq = seq[-1]
    else:
        last_seq = seq

    last_conv = get_last_layer_name(last_seq)
    feature_channels = getattr(last_seq, last_conv).out_channels
    return feature_channels


def get_last_layer_name(layer, prefix="conv", max_layer=10):
    last_conv_name = None
    for i in range(max_layer, 1, -1):
        if hasattr(layer, f"{prefix}{i}"):
            last_conv_name = f"{prefix}{i}"
            break
    return last_conv_name