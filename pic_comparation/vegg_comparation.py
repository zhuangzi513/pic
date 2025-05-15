import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import numpy as np

# 加载预训练的VGG模型
vgg = models.vgg16(pretrained=True)
vgg.eval()  # 设置为评估模式

# 定义特征提取器
class FeatureExtractor(nn.Module):
    def __init__(self, model):
        super(FeatureExtractor, self).__init__()
        self.model = model
        self.feature = nn.Sequential(*list(self.model.children())[:-1])  # 移除最后的分类层

    def forward(self, x):
        return self.feature(x)

# 创建特征提取器
extractor = FeatureExtractor(vgg)

# 图片预处理
transform = transforms.Compose([
    transforms.Resize((224, 224)),  # VGG输入尺寸
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# 加载图片
def load_image(image_path):
    image = Image.open(image_path).convert('RGB')
    image = transform(image).unsqueeze(0)  # 添加批次维度
    return image

# 计算特征向量
def get_features(image):
    with torch.no_grad():
        features = extractor(image)
    return features.view(features.size(0), -1)  # 展平特征向量

# 计算相似度
def calculate_similarity(features1, features2):
    similarity = torch.cosine_similarity(features1, features2)
    return similarity.item()

# 示例使用
if __name__ == "__main__":
    image_path1 = "image1.jpg"
    image_path2 = "image2.jpg"

    image1 = load_image(image_path1)
    image2 = load_image(image_path2)

    features1 = get_features(image1)
    features2 = get_features(image2)

    similarity = calculate_similarity(features1, features2)
    print(f"Similarity between the two images: {similarity:.4f}")
