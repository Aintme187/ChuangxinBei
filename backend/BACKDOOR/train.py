import torch
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, random_split

from torchvision import models
import torch.nn as nn

import torch.optim as optim
from sklearn.metrics import accuracy_score

from tqdm import tqdm

# 数据预处理
transform = transforms.Compose([
    transforms.Resize((224, 224)),  # 调整图片大小以适应ResNet
    transforms.ToTensor()
])

# 加载数据集
dataset = datasets.ImageFolder('../data/lfw', transform=transform)

# 划分数据集
# train_size = int(0.8 * len(dataset))
# test_size = len(dataset) - train_size
# train_dataset, test_dataset = random_split(dataset, [train_size, test_size])

train_size = int(0.01 * len(dataset))
test_size = len(dataset) - train_size
train_dataset, test_dataset = random_split(dataset, [train_size, test_size])
test_dataset = train_dataset

# 创建数据加载器
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=32)

# 加载预训练的ResNet模型
model = models.resnet18(pretrained=True)

# 更改最后一层以匹配类别数
num_classes = len(dataset.classes)
model.fc = nn.Linear(model.fc.in_features, num_classes)

# 检查是否有可用的GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)


# 定义损失函数和优化器
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 训练模型
num_epochs = 10  # 可以根据需要调整

for epoch in range(num_epochs):
    model.train()
    running_loss = 0.0
    train_bar = tqdm(train_loader, desc=f'Epoch {epoch+1}/{num_epochs} [Train]')

    for images, labels in train_bar:
        images, labels = images.to(device), labels.to(device)

        # 前向传播和反向传播
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        # train_bar.set_postfix(loss=(running_loss / (train_bar.iterable.i + 1)))
        train_bar.set_postfix(loss=(running_loss / (train_bar.n + 1)))

    # 计算平均损失
    epoch_loss = running_loss / len(train_loader)
    print(f'Epoch {epoch+1}, Average Loss: {epoch_loss}')

    # 验证模型
    model.eval()
    all_labels = []
    all_preds = []
    test_bar = tqdm(test_loader, desc=f'Epoch {epoch+1}/{num_epochs} [Test]')

    with torch.no_grad():
        for images, labels in test_bar:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            all_labels.extend(labels.cpu().numpy())
            all_preds.extend(predicted.cpu().numpy())

    # 计算准确率
    accuracy = accuracy_score(all_labels, all_preds)
    print(f'Accuracy: {accuracy * 100}%')
