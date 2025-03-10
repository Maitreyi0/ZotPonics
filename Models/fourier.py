import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms, datasets
from torch.utils.data import DataLoader
import cv2
import numpy as np
from PIL import Image


class LeafSegmentation(object):

    def __call__(self, img):
        img_np = np.array(img)
        img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)
        lower_green = np.array([25, 40, 40])
        upper_green = np.array([85, 255, 255])
        mask = cv2.inRange(hsv, lower_green, upper_green)
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        segmented = cv2.bitwise_and(img_cv, img_cv, mask=mask)
        segmented = cv2.cvtColor(segmented, cv2.COLOR_BGR2RGB)
        return Image.fromarray(segmented)


def conv_block(in_channels, out_channels, pool=True):
    """
    convolutional block:
      - 2D conv (kernel size 3, stride 1, padding 1)
      - Batch norm
      - ReLU
      - max pool
    """
    layers = [
        nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=1, padding=1),
        nn.BatchNorm2d(out_channels),
        nn.ReLU(inplace=True)
    ]
    if pool:
        layers.append(nn.MaxPool2d(2))
    return nn.Sequential(*layers)


class SpinachLeafFCN(nn.Module):
    def __init__(self, num_classes=5, hist_bins=16):
        super(SpinachLeafFCN, self).__init__()
        self.hist_bins = hist_bins

        self.register_buffer('mean', torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1))
        self.register_buffer('std', torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1))

        self.conv1 = conv_block(3, 32, pool=True)
        self.conv2 = conv_block(32, 64, pool=True)
        self.conv3 = conv_block(64, 128, pool=True)
        self.conv4 = conv_block(128, 256, pool=True)
        self.conv5 = conv_block(256, 512, pool=True)
        self.conv6 = conv_block(512, 512, pool=False)
        self.conv7 = conv_block(512, 512, pool=False)
        self.conv8 = conv_block(512, 512, pool=False)
        self.conv9 = conv_block(512, 512, pool=False)
        self.conv10 = conv_block(512, 512, pool=False)

        self.global_pool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Sequential(
            nn.Linear(512 + 3 * hist_bins, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes)
        )

    def compute_histogram(self, x):
        x_orig = x * self.std + self.mean
        batch_size = x_orig.size(0)
        hist_list = []
        for i in range(batch_size):
            channel_histograms = []
            for c in range(3):
                channel = x_orig[i, c, :, :]
                hist = torch.histc(channel, bins=self.hist_bins, min=0.0, max=1.0)
                hist = hist / (channel.numel() + 1e-6)
                channel_histograms.append(hist)
            hist_img = torch.cat(channel_histograms)
            hist_list.append(hist_img)
        hist_features = torch.stack(hist_list, dim=0)  # shape: (B, 3*hist_bins)
        return hist_features

    def forward(self, x):
        out = self.conv1(x)
        out = self.conv2(out)
        out = self.conv3(out)
        out = self.conv4(out)
        out = self.conv5(out)
        out = self.conv6(out)
        out = self.conv7(out)
        out = self.conv8(out)
        out = self.conv9(out)
        out = self.conv10(out)
        out = self.global_pool(out)
        cnn_features = out.view(out.size(0), -1)

        hist_features = self.compute_histogram(x)

        combined_features = torch.cat([cnn_features, hist_features], dim=1)
        out = self.fc(combined_features)
        return out



if __name__ == '__main__':
    transform = transforms.Compose([
        LeafSegmentation(),
        transforms.Resize((512, 512)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])

    dataset = datasets.ImageFolder(root="Malabar_Dataset", transform=transform)
    dataloader = DataLoader(dataset, batch_size=8, shuffle=True, num_workers=12)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = SpinachLeafFCN(num_classes=5, hist_bins=16).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.006)

    num_epochs = 100
    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        for inputs, labels in dataloader:
            inputs = inputs.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * inputs.size(0)
            print(f"\t\tLoss: {loss.item():.4f}")
        epoch_loss = running_loss / len(dataset)
        print(f"Epoch {epoch + 1}/{num_epochs}, Loss: {epoch_loss:.4f}")

    torch.save(model.state_dict(), "fourier_conv.pth")
