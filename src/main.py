from model import UNet
from data import train_test_filenames
from skimage import io, transform
import torch
from torch.utils.data import Dataset, DataLoader
import torch.nn as nn
import torch.optim as optim
from torch.optim import lr_scheduler
from torchvision import transforms
import matplotlib.pyplot as plt
import time



class ShapesDataset(Dataset):

    def __init__(self, input_paths, output_paths, transform=None):

        self.input_paths = input_paths
        self.output_paths = output_paths
        self.transform = transform

    def __len__(self):
        return len(self.input_paths)

    def __getitem__(self, idx):
        input_path = './'+self.input_paths[idx]
        input_image = io.imread(input_path).transpose((2, 0, 1))
        input_tensor = torch.from_numpy(input_image).double()
        output_path = './'+self.output_paths[idx]
        output_image = io.imread(output_path).transpose((2, 0, 1))
        output_tensor = torch.from_numpy(output_image).double()

        sample = {'input': input_tensor, 'output': output_tensor}


        return sample

data_transform = transforms.Compose([transforms.ToTensor()])
train_input, test_input, train_output, test_output = train_test_filenames()

train_dataset = ShapesDataset(train_input, train_output, None)
test_dataset = ShapesDataset(test_input, test_output, None)

'''for i in range(len(train_dataset)):
    sample = train_dataset[i]

    print(i, sample['input'].shape, sample['output'].shape)

    ax = plt.subplot(2, 4, i + 1)
    plt.tight_layout()
    ax.set_title('Sample #{}'.format(i))
    ax.axis('off')
    ax.imshow(sample['input'])

    ax = plt.subplot(2, 4, i + 5)
    plt.tight_layout()
    ax.set_title('Sample #{}'.format(i))
    ax.axis('off')
    ax.imshow(sample['output'])

    if i == 3:
        plt.show()
        break'''

dataloader = DataLoader(train_dataset, batch_size=4,
                        shuffle=True, num_workers=4)
model = UNet()
criterion = nn.MSELoss()
optimizer = optim.SGD(model.parameters(), lr=0.001, momentum=0.9)
exp_lr_scheduler = lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)


def train_model(model, criterion, optimizer, scheduler, num_epochs, device):
    since = time.time()

    for epoch in range(num_epochs):
        print('Epoch {}/{}'.format(epoch, num_epochs - 1))
        print('-' * 10)

        scheduler.step()
        model.train()  # Set model to training mode

        running_loss = 0.0
        running_corrects = 0

        # Iterate over data.
        for d in dataloader:
            print(d.keys())
            inputs = d['input'].float().to(device)
            depths = d['output'].float().to(device)

            # zero the parameter gradients
            optimizer.zero_grad()

            # forward
            # track history if only in train
            with torch.set_grad_enabled(True):
                outputs = model(inputs)
                loss = criterion(outputs, depths)

                # backward + optimize only if in training phase
                loss.backward()
                optimizer.step()

            # statistics
            running_loss += loss.item() * inputs.size(0)

        epoch_loss = running_loss

        print('{} Loss: {:.4f}'.format(
            phase, epoch_loss))

        print()
        return model

    time_elapsed = time.time() - since
    print('Training complete in {:.0f}m {:.0f}s'.format(
        time_elapsed // 60, time_elapsed % 60))

model = train_model(model, criterion, optimizer, exp_lr_scheduler,
                       num_epochs=1, device='cuda')
