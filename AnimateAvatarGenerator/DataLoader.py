import torch
import torchvision.datasets as dset
import torchvision.transforms as transforms
import pandas as pd
import os
import numpy as np
from PIL import Image

from skimage import io
# We can use an image folder dataset the way we have it setup.
# Create the dataset

def get_dataloader( dir_path, batch_size = 128, image_size = 64, shuffle = True, workers = 2):
    dataset = dset.ImageFolder(dir_path,
                            transform=transforms.Compose([
                                transforms.Resize(image_size),
                                transforms.CenterCrop(image_size),
                                transforms.ToTensor(),
                                transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
                            ]))
    # Create the dataloader
    dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size,
                                            shuffle=True, num_workers=workers)

    return dataloader


class MyDataSet( torch.utils.data.Dataset):
    def __init__( self, csv_file, root_dir, transform = None):
        self.data_frame = pd.read_csv( csv_file, header = None)
        self.data_frame.iloc[:,0] = self.data_frame.iloc[:,0].apply( lambda x : f"{int(x)}.jpg")
        # print( self.data_frame.sample(10) ) 

        self.root_dir = root_dir
        self.transform = transform

    def __len__( self):
        return len( self.data_frame)

    def __getitem__(self, index):
        if torch.is_tensor( index):
            index = index.tolist()
            
        image_name = self.data_frame.iloc[ index , 0 ]
        
        X = Image.open( os.path.join( self.root_dir, image_name) )
        Y = np.array( self.data_frame.iloc[ index,1:] ).astype( np.float)
        z = image_name
        if self.transform is not None:
            X = self.transform( X)
        return  X, torch.tensor( Y)