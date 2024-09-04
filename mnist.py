import argparse
# import os.path
import os
import torch
import cv2
import numpy as np
from pathlib import Path
# 确定文件所在目录的绝对路径
parentpath = Path(__file__).absolute().parent

# 调用作业三中训练得到的LeNet图片分类模板
# 返回“Classification result: {result}”的分类结果
def image_classification(file):
    if not os.path.isfile(file):
        raise ValueError("File does not exist or is not a file.")
    # 加载预训练的 LeNet 模型
    model = LeNet()
    modelpath = parentpath / "lenet.pth"
    if not os.path.exists(modelpath):
        raise ValueError(f'modelpath is invalid:{modelpath}')

    # 安全地加载状态字典
    load_dict = torch.load(modelpath)
    model.load_state_dict(load_dict, strict=False)

    # 使用 OpenCV 读取指定路径图像
    img = cv2.imread(file)
    # print(file)
    if img is None:
        raise ValueError("Image not found")
    # 将图像传入模型进行推理，并获取预测结果label
    label = inference(model, img)
    result = "Classification result: {}".format(label)
    return result

# 引用自作业3 models/lenet.py
# 通过三个卷积层提取特征，然后通过一个全连接层进行分类。
# 网络能够处理输入图像并将其分类到预定义的类别中。
class LeNet(torch.nn.Module):
    def __init__(self, num_classes=10):
        super(LeNet, self).__init__()

        self.layer1 = torch.nn.Sequential(
            torch.nn.Conv2d(1, 16, kernel_size=5, stride=1, padding=2),
            torch.nn.BatchNorm2d(16),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(kernel_size=2, stride=2))
        self.layer2 = torch.nn.Sequential(
            torch.nn.Conv2d(16, 32, kernel_size=5, stride=1, padding=2),
            torch.nn.BatchNorm2d(32),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(kernel_size=2, stride=2))

        self.layer3 = torch.nn.Sequential(
            torch.nn.Conv2d(32, 64, kernel_size=5, stride=1, padding=2),
            torch.nn.BatchNorm2d(64),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(kernel_size=2, stride=2))

        self.fc = torch.nn.Linear(3 * 3 * 64, num_classes)

    def forward(self, x):
        out = self.layer1(x)
        out = self.layer2(out)
        if self.layer3 is not None:
            out = self.layer3(out)
        out = out.reshape(out.size(0), -1)
        out = self.fc(out)
        return out

# 引用自作业3 models/inference.py
def pre_process(img, device):
    if img is None:
        raise ValueError("Image not found or unable to load.")
    else:
        img = cv2.resize(img, (28, 28))
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        img = img / 255
        img = np.ascontiguousarray(img)
        img = torch.from_numpy(img).to(device)
        img = img.float()
        img = img.unsqueeze(0)
        if img.ndimension() == 3:
            img = img.unsqueeze(0)
        return img


def inference(model, img):
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    img = pre_process(img, device)
    model.to(device)
    model.eval()
    preds = model(img)
    # preds is the outputs for a batch
    label = preds[0].argmax()
    return label

if __name__ == "__main__":
    output = image_classification("mnist.png")
    print(output)