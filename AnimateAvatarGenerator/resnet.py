import torch

from torch import nn


class BasicBlock( nn.Module):
    def __init__( self, in_planes = 3, out_planes = 64, stride = 1, downsample = None):
        super().__init__()

        self.model = nn.Sequential(
            nn.Conv2d( in_planes, out_planes, 3, stride, 1, bias = False),
            nn.BatchNorm2d( out_planes),
            nn.LeakyReLU( 0.2),

            nn.Conv2d( out_planes, out_planes, 3, 1, 1, bias = False),
            nn.BatchNorm2d( out_planes),
        )

        self.downsample = downsample
        self.activation = nn.LeakyReLU( 0.2)
    
    def forward( self, X):
        identity = X
        if self.downsample is not None:
            identity = self.downsample( X)
        return self.activation( self.model( X) + identity )


class ResNetDiscriminator( nn.Module):
    def __init__(self, c_dim = 64, hair_dim = 12, eye_dim = 11):
        super().__init__()

        # 3,64,64 -> 64, 64, 64
        self.conv = nn.Sequential(
            nn.Conv2d( 3, c_dim, 5, 1, 2, bias = False),
            nn.BatchNorm2d( c_dim),
            nn.LeakyReLU( 0.2)
            # maxpoll
        )

        # 
        self.middle = nn.Sequential(
            self._make_layer( c_dim, c_dim),
            self._make_layer( c_dim, c_dim * 2),
            self._make_layer( c_dim * 2, c_dim * 4),
            self._make_layer( c_dim * 4, c_dim * 8),
        )
        # 64,32,32 -> 64 * 8, 4, 4

        # self.avgpool
        self.avgpool = nn.AdaptiveAvgPool2d((1,1))

        # layers for authenticity
        self.fc_authen = nn.Sequential(
            nn.Linear( c_dim * 8 , 1),
            nn.Sigmoid() )
        nn.Linear( c_dim * 8 , 1)

        # layers for hair
        self.fc_hair = nn.Sequential(
            nn.Linear( c_dim * 8 , hair_dim),
            nn.Sigmoid() )

        # layers for eye
        self.fc_eye = nn.Sequential(
            nn.Linear( c_dim * 8 , eye_dim),
            nn.Sigmoid() )


    def forward( self, X):
        a1 = self.conv( X)
        a2 = self.middle( a1)
        a3 = torch.flatten( self.avgpool( a2), 1)
        scores_authen = self.fc_authen( a3).viwe( len(X), -1 )
        scores_hair = self.fc_hair( a3)
        scores_eye = self.fc_eye( a3)
        return scores_authen, scores_hair, scores_eye


    def _make_layer( self, in_dim, out_dim, cur_layers_cnt = 2, block = BasicBlock):

        # stride = 2
        # if stride > 1 or in_dim != out_dim
        downsample = nn.Sequential(
            nn.Conv2d( in_dim, out_dim, 1, 2, bias = False),
            nn.BatchNorm2d( out_dim)
        )

        cur_layers = []
        cur_layers.append( block( in_dim, out_dim, 2, downsample) )

        for i in range( 1, cur_layers_cnt):
            cur_layers.append( block( out_dim, out_dim) )
        
        return nn.Sequential( *cur_layers)



class MiddleBlock( nn.Module):
    def __init__( self):
        super().__init__()
        self.model = nn.Sequential(
            nn.Conv2d( 64, 64, 3, 1, 1, bias=False),
            nn.BatchNorm2d( 64),
            nn.ReLU(),

            nn.Conv2d( 64, 64, 3, 1, 1, bias=False),
            nn.BatchNorm2d( 64)
        )

        # New Add
        self.activation = nn.Relu()
    def forward( self, X):

        # temp
        return self.activation( X + self.model( X) )


class shuffle( nn.Module):
    def __init__(self):
        super().__init__()

    def forward( self, X, scale = 2):
        N, C, W, H= X.shape
        def foo( x):
            return x.view( N, W, H, scale, scale).permute( 0, 1, 3, 2, 4).contiguous().view( N, 1, H * scale, W * scale)
        return torch.cat( [ foo(x) for x in X.permute( 0, 2, 3, 1).split( scale ** 2, dim = 3) ] , dim = 1 )

        
class TailBlock( nn.Module):
    def __init__(self, in_c = 64, out_c = 256):
        super().__init__()

        self.model = nn.Sequential(
            nn.Conv2d( in_c, out_c, 3, 1, 1, bias=False),
            shuffle(),
            nn.BatchNorm2d( in_c),
            nn.ReLU()
        )
    def forward( self, X):
        return self.model( X)


class ResNetGenerator( nn.Module):
    def __init__(self):
        super().__init__()

        self.layer1 = nn.Sequential(
            nn.Linear( 123, 64 *8 *8),
            nn.BatchNorm1d( 64 * 8 * 8),
            nn.ReLU()
        )

        self.layer2 = nn.Sequential(
            * ( [ MiddleBlock() for _ in range( 16)] + [ 
                # nn.BatchNorm2d( 64),
                # nn.ReLU()
            ] )
        )

        self.layer3 = nn.Sequential(
            *( [ TailBlock() for _ in range(3)] + [
                nn.Conv2d( 64, 3, 9, 1, 4),
                nn.Tanh()
            ])
        )

    def forward( self, cur_input):
        a1 = self.layer1( cur_input).view( -1, 64, 8, 8)
        a2 = self.lay2( a1)
        # a2 = self.layer2( a1) + a1
        return self.layer3( a2)