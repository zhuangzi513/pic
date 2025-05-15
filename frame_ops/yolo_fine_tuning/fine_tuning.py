import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import numpy as np
from ultralytics import YOLO

g_batch_size = 4
g_num_workers = 1
_num_epochs = 10
_device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
_model = YOLO('yolo11n.pt')
_model.to(_device)
_optimizer = torch.optim.Adam(_model.parameters(), lr=0.01)
_criterion = nn.CrossEntropyLoss()

_train_transform = transforms.Compose([
    transforms.Resize((640, 640)),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    #transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

_val_transform = transforms.Compose([
    transforms.Resize((640, 640)),
    transforms.ToTensor(),
    #transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

class YOLODataset(Dataset):
    def __init__(self, image_dir, label_dir, transform=None):
        self.image_dir = image_dir
        self.label_dir = label_dir
        self.transform = transform
        self.images = os.listdir(image_dir)

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img_path = os.path.join(self.image_dir, self.images[idx])
        label_path = os.path.join(self.label_dir, self.images[idx].replace('.jpg', '.txt'))
        print("get item:", img_path)
        print("get item:", label_path)

        image = Image.open(img_path).convert('RGB')
        labels = np.loadtxt(label_path).reshape(-1, 5)
        print("get item labels:", labels)

        if self.transform:
            image = self.transform(image)

        return image, labels

_train_dataset = YOLODataset(image_dir='../dataset/images/train', label_dir='../dataset/labels/train', transform=_train_transform)
_val_dataset = YOLODataset(image_dir='../dataset/images/val', label_dir='../dataset/labels/val', transform=_val_transform)

_train_loader = DataLoader(_train_dataset, batch_size=g_batch_size, shuffle=True, num_workers=g_num_workers)
_val_loader = DataLoader(_val_dataset, batch_size=g_batch_size, shuffle=False, num_workers=g_num_workers)

for param in _model.parameters():
    param.requires_grad = False

for param in _model.model.model[-1].parameters():
    param.requires_grad = True

def train_one_epoch(model, train_loader, optimizer, device):
    #model.train(data="data.yaml")
    running_loss = 0.0
    for images, labels in train_loader:
        images = images.to(device)
        labels = labels.to(device)
        print("t input images:", images.shape)
        print("t input labels:", labels.shape)

        optimizer.zero_grad()
        print("calling torch.tensor(model(images))")
        outputs = model(images)
        print("t o labels:", labels.shape)
        print("t o outputs:", outputs)
        #loss = _criterion(outputs, labels)
        #loss.backward()
        #optimizer.step()
        #running_loss += loss.item()
    return running_loss / len(train_loader)

def validate(model, val_loader, device):
    model.eval()
    total_loss = 0.0
    with torch.no_grad():
        for images, labels in val_loader:
            images = images.to(device)
            labels = labels.to(device)
            outputs = torch.tensor(model(images)).to(device)
            print("v labels:", labels)
            print("v outputs:",outputs)
            loss = _criterion(outputs, labels)
            total_loss += loss.item()
    return total_loss / len(val_loader)

for epoch in range(_num_epochs):
    print("calling train_one_epoch")
    train_loss = train_one_epoch(_model, _train_loader, _optimizer, _device)
    val_loss = validate(_model, _val_loader, _device)
    print(f"Epoch [{epoch+1}/{num_epochs}], Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")

torch.save(_model.state_dict(), 'yolov11_finetuned.pt')
