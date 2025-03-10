import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models, datasets, transforms
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



transform = transforms.Compose([
    LeafSegmentation(),
    transforms.Resize((1000, 1000)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

data_dir = 'Malabar_Dataset'
dataset = datasets.ImageFolder(root=data_dir, transform=transform)
batch_size = 8
dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=4)


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    num_classes = 5

    from torchvision.models import resnet50, ResNet50_Weights
    weights = ResNet50_Weights.IMAGENET1K_V1
    model = resnet50(weights=weights)

    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, num_classes)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.006)

    num_epochs = 100

    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        for inputs, labels in dataloader:
            inputs, labels = inputs.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * inputs.size(0)
            print(f"\tEpoch {epoch + 1}/{num_epochs}, Loss: {loss.item():.4f}")
        epoch_loss = running_loss / len(dataset)
        print(f"Epoch {epoch + 1}/{num_epochs}, Loss: {epoch_loss:.4f}")

    torch.save(model.state_dict(), "leaf_classifier.pth")


if __name__ == '__main__':
    main()
