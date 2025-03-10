import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms, datasets
from torch.utils.data import DataLoader
import cv2
import numpy as np
from PIL import Image


# =============================================================================
# 1. Custom Transform for Leaf Segmentation
# =============================================================================
class LeafSegmentation(object):
    """
    Custom transform to segment the leaf from the background.
    This implementation uses simple HSV thresholding (assuming the leaf is predominantly green).
    Adjust lower_green and upper_green as needed.
    """

    def __call__(self, img):
        # Convert the PIL image to a NumPy array (RGB)
        img_np = np.array(img)
        # Convert from RGB to BGR (since OpenCV uses BGR)
        img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        # Convert image to HSV color space
        hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)
        # Define HSV range for green (tweak these values for your dataset)
        lower_green = np.array([25, 40, 40])
        upper_green = np.array([85, 255, 255])
        # Create a mask for green regions
        mask = cv2.inRange(hsv, lower_green, upper_green)
        # Clean up the mask with a morphological operation
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        # Apply the mask to the original image
        segmented = cv2.bitwise_and(img_cv, img_cv, mask=mask)
        # Convert back from BGR to RGB
        segmented = cv2.cvtColor(segmented, cv2.COLOR_BGR2RGB)
        return Image.fromarray(segmented)


# =============================================================================
# 2. Helper Function for Convolutional Blocks
# =============================================================================
def conv_block(in_channels, out_channels, pool=True):
    """
    Builds a convolutional block with:
      - 2D convolution (kernel size 3, stride 1, padding 1)
      - Batch normalization
      - ReLU activation
      - Optional 2x2 max pooling
    """
    layers = [
        nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=1, padding=1),
        nn.BatchNorm2d(out_channels),
        nn.ReLU(inplace=True)
    ]
    if pool:
        layers.append(nn.MaxPool2d(2))  # Reduce spatial dimensions by a factor of 2
    return nn.Sequential(*layers)


# =============================================================================
# 3. Deep FCN Model with Histogram Fusion
# =============================================================================
class SpinachLeafFCN(nn.Module):
    def __init__(self, num_classes=5, hist_bins=16):
        """
        Args:
            num_classes (int): Number of classes (here, 5).
            hist_bins (int): Number of bins per channel for the RGB histogram.
                             Total histogram feature size will be 3 * hist_bins.
        """
        super(SpinachLeafFCN, self).__init__()
        self.hist_bins = hist_bins

        # Register the normalization parameters as buffers (for un-normalizing input when computing histograms)
        # These are the ImageNet mean and std used in our normalization.
        self.register_buffer('mean', torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1))
        self.register_buffer('std', torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1))

        # Build a deep convolutional branch using more than 10 layers.
        # We use pooling for the first five blocks to gradually reduce spatial dimensions.
        self.conv1 = conv_block(3, 32, pool=True)  # Output: 32 x 1000/2=500 x 500
        self.conv2 = conv_block(32, 64, pool=True)  # 64 x 500/2=250 x 250
        self.conv3 = conv_block(64, 128, pool=True)  # 128 x 250/2=125 x 125
        self.conv4 = conv_block(128, 256, pool=True)  # 256 x 125/2=62 x 62 (approx.)
        self.conv5 = conv_block(256, 512, pool=True)  # 512 x 62/2=31 x 31 (approx.)
        # For further depth, add additional conv blocks without pooling
        self.conv6 = conv_block(512, 512, pool=False)  # 512 x 31 x 31
        self.conv7 = conv_block(512, 512, pool=False)  # 512 x 31 x 31
        self.conv8 = conv_block(512, 512, pool=False)  # 512 x 31 x 31
        self.conv9 = conv_block(512, 512, pool=False)  # 512 x 31 x 31
        self.conv10 = conv_block(512, 512, pool=False)  # 512 x 31 x 31

        # Global average pooling to collapse the spatial dimensions
        self.global_pool = nn.AdaptiveAvgPool2d((1, 1))  # Output: 512 x 1 x 1

        # The histogram branch computes a 3*hist_bins feature vector.
        # Concatenate CNN features (512) with histogram features (3*hist_bins)
        self.fc = nn.Sequential(
            nn.Linear(512 + 3 * hist_bins, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes)
        )

    def compute_histogram(self, x):
        """
        Compute a normalized RGB histogram for each image in the batch.
        Args:
            x (Tensor): Batch of images of shape (B, 3, H, W). These are normalized images.
        Returns:
            Tensor: Histogram features of shape (B, 3 * hist_bins)
        """
        # Un-normalize to recover pixel values in [0,1]
        x_orig = x * self.std + self.mean  # shape: (B, 3, H, W)
        batch_size = x_orig.size(0)
        hist_list = []
        for i in range(batch_size):
            channel_histograms = []
            for c in range(3):
                channel = x_orig[i, c, :, :]
                # Compute histogram with hist_bins in the range [0,1]
                hist = torch.histc(channel, bins=self.hist_bins, min=0.0, max=1.0)
                hist = hist / (channel.numel() + 1e-6)
                channel_histograms.append(hist)
            # Concatenate histograms from the three channels -> (3*hist_bins,)
            hist_img = torch.cat(channel_histograms)
            hist_list.append(hist_img)
        hist_features = torch.stack(hist_list, dim=0)  # shape: (B, 3*hist_bins)
        return hist_features

    def forward(self, x):
        # CNN branch: extract deep spatial features.
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
        out = self.global_pool(out)  # shape: (B, 512, 1, 1)
        cnn_features = out.view(out.size(0), -1)  # shape: (B, 512)

        # Histogram branch: compute RGB histograms.
        hist_features = self.compute_histogram(x)  # shape: (B, 3*hist_bins)

        # Concatenate the features from both branches.
        combined_features = torch.cat([cnn_features, hist_features], dim=1)
        out = self.fc(combined_features)
        return out


# =============================================================================
# 4. Data Pipeline and Training Loop
# =============================================================================
if __name__ == '__main__':
    # Transformation pipeline:
    # 1. LeafSegmentation to mask out the background.
    # 2. Resize images to 1000x1000.
    # 3. Convert to tensor and normalize using ImageNet stats.
    transform = transforms.Compose([
        LeafSegmentation(),
        transforms.Resize((512, 512)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])

    # Load the dataset from the "Malabar_Dataset" folder (each subfolder is a class)
    dataset = datasets.ImageFolder(root="Malabar_Dataset", transform=transform)
    dataloader = DataLoader(dataset, batch_size=8, shuffle=True, num_workers=12)

    # Set up device (GPU if available)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Instantiate the model and move it to the device
    model = SpinachLeafFCN(num_classes=5, hist_bins=16).to(device)

    # Define loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.006)

    # Training loop (for demonstration, run for 10 epochs)
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

    # Save the trained model
    torch.save(model.state_dict(), "spinach_leaf_fcn_deep.pth")
