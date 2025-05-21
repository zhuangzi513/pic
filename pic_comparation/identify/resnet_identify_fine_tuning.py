import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as transforms
import torchvision.datasets as datasets
import torchvision.models as models
from torch.utils.data import DataLoader, Dataset
import numpy as np
from PIL import Image
import os
from tqdm import tqdm
import random
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

# Set random seeds for reproducibility
torch.manual_seed(42)
np.random.seed(42)
random.seed(42)

# Device configuration
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# Hyperparameters
batch_size = 32
num_epochs = 20
learning_rate = 0.001
margin = 1.0  # Margin for triplet loss
embedding_size = 128  # Size of the embedding vector

# Dataset paths (modify these to your dataset)
train_dir = 'data/train'
test_dir = 'data/test'

# Data preprocessing
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Custom dataset for triplet sampling
class TripletDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.classes = os.listdir(root_dir)
        self.class_to_idx = {cls_name: idx for idx, cls_name in enumerate(self.classes)}
        self.idx_to_class = {idx: cls_name for idx, cls_name in enumerate(self.classes)}
        self.image_paths = []
        
        for cls_name in self.classes:
            cls_path = os.path.join(root_dir, cls_name)
            for img_name in os.listdir(cls_path):
                self.image_paths.append((os.path.join(cls_path, img_name), self.class_to_idx[cls_name]))
    
    def __getitem__(self, index):
        anchor_path, anchor_label = self.image_paths[index]
        
        # Find positive sample (same class)
        positive_indices = [i for i, (_, label) in enumerate(self.image_paths) 
                          if label == anchor_label and i != index]
        positive_index = random.choice(positive_indices)
        positive_path, _ = self.image_paths[positive_index]
        
        # Find negative sample (different class)
        negative_indices = [i for i, (_, label) in enumerate(self.image_paths) 
                          if label != anchor_label]
        negative_index = random.choice(negative_indices)
        negative_path, _ = self.image_paths[negative_index]
        
        # Load images
        anchor_img = Image.open(anchor_path).convert('RGB')
        positive_img = Image.open(positive_path).convert('RGB')
        negative_img = Image.open(negative_path).convert('RGB')
        
        if self.transform:
            anchor_img = self.transform(anchor_img)
            positive_img = self.transform(positive_img)
            negative_img = self.transform(negative_img)
        
        return anchor_img, positive_img, negative_img, anchor_label
    
    def __len__(self):
        return len(self.image_paths)

# Create datasets and dataloaders
train_dataset = TripletDataset(train_dir, transform=transform)
test_dataset = datasets.ImageFolder(test_dir, transform=transform)

train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

# Model definition
class ResNetTriplet(nn.Module):
    def __init__(self, embedding_size=128, pretrained=True):
        super(ResNetTriplet, self).__init__()
        self.resnet = models.resnet50(pretrained=pretrained)
        
        # Remove the final fully connected layer
        self.resnet = nn.Sequential(*list(self.resnet.children())[:-1])
        
        # Add custom embedding layer
        self.fc = nn.Sequential(
            nn.Linear(2048, 1024),
            nn.BatchNorm1d(1024),
            nn.ReLU(),
            nn.Linear(1024, embedding_size)
        )
    
    def forward(self, x):
        x = self.resnet(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        # L2 normalize the embeddings
        x = nn.functional.normalize(x, p=2, dim=1)
        return x

# Triplet loss function
class TripletLoss(nn.Module):
    def __init__(self, margin=1.0):
        super(TripletLoss, self).__init__()
        self.margin = margin
    
    def forward(self, anchor, positive, negative):
        distance_positive = (anchor - positive).pow(2).sum(1)  # Euclidean distance squared
        distance_negative = (anchor - negative).pow(2).sum(1)
        losses = torch.relu(distance_positive - distance_negative + self.margin)
        return losses.mean()

# Initialize model, loss, and optimizer
model = ResNetTriplet(embedding_size=embedding_size).to(device)
criterion = TripletLoss(margin=margin)
optimizer = optim.Adam(model.parameters(), lr=learning_rate)

# Training loop
def train_model(model, train_loader, criterion, optimizer, num_epochs):
    model.train()
    for epoch in range(num_epochs):
        running_loss = 0.0
        progress_bar = tqdm(train_loader, desc=f'Epoch {epoch+1}/{num_epochs}')
        
        for batch_idx, (anchor, positive, negative, _) in enumerate(progress_bar):
            anchor = anchor.to(device)
            positive = positive.to(device)
            negative = negative.to(device)
            
            # Forward pass
            anchor_emb = model(anchor)
            positive_emb = model(positive)
            negative_emb = model(negative)
            
            # Compute loss
            loss = criterion(anchor_emb, positive_emb, negative_emb)
            
            # Backward pass and optimize
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            progress_bar.set_postfix(loss=running_loss/(batch_idx+1))
        
        print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {running_loss/len(train_loader):.4f}')

# Evaluation function using KNN
def evaluate_model(model, train_loader, test_loader):
    model.eval()
    
    # Extract embeddings and labels from training set
    train_features = []
    train_labels = []
    with torch.no_grad():
        for images, labels in tqdm(train_loader, desc='Extracting train embeddings'):
            images = images.to(device)
            features = model(images)
            train_features.append(features.cpu().numpy())
            train_labels.append(labels.numpy())
    
    train_features = np.concatenate(train_features)
    train_labels = np.concatenate(train_labels)
    
    # Extract embeddings and labels from test set
    test_features = []
    test_labels = []
    with torch.no_grad():
        for images, labels in tqdm(test_loader, desc='Extracting test embeddings'):
            images = images.to(device)
            features = model(images)
            test_features.append(features.cpu().numpy())
            test_labels.append(labels.numpy())
    
    test_features = np.concatenate(test_features)
    test_labels = np.concatenate(test_labels)
    
    # Train KNN classifier
    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(train_features, train_labels)
    
    # Predict and calculate accuracy
    pred_labels = knn.predict(test_features)
    accuracy = accuracy_score(test_labels, pred_labels)
    
    print(f'Test Accuracy: {accuracy*100:.2f}%')
    return accuracy

# Train the model
print("Starting training...")
train_model(model, train_loader, criterion, optimizer, num_epochs)

# Evaluate the model
print("Evaluating model...")
evaluate_model(model, train_loader, test_loader)

# Save the model
torch.save(model.state_dict(), 'resnet_triplet.pth')
print("Model saved to resnet_triplet.pth")
