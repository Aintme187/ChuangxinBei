import time
import os
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset
from torchvision import datasets, transforms
import pickle
import PIL.Image as Image


class LeNet(nn.Module):
    def __init__(self, channel=3, hideen=768, num_classes=10):
        super(LeNet, self).__init__()
        act = nn.Sigmoid
        self.body = nn.Sequential(
            nn.Conv2d(channel, 12, kernel_size=5, padding=5 // 2, stride=2),
            act(),
            nn.Conv2d(12, 12, kernel_size=5, padding=5 // 2, stride=2),
            act(),
            nn.Conv2d(12, 12, kernel_size=5, padding=5 // 2, stride=1),
            act(),
        )
        self.fc = nn.Sequential(
            nn.Linear(hideen, num_classes)
        )

    def forward(self, x):
        out = self.body(x)
        out = out.view(out.size(0), -1)
        # print(out.size())
        # print(x)
        out = self.fc(out)
        return out


def weights_init(m):
    try:
        if hasattr(m, "weight"):
            m.weight.data.uniform_(-0.5, 0.5)
    except Exception:
        print('warning: failed in weights_init for %s.weight' % m._get_name())
    try:
        if hasattr(m, "bias"):
            m.bias.data.uniform_(-0.5, 0.5)
    except Exception:
        print('warning: failed in weights_init for %s.bias' % m._get_name())


class Dataset_from_Image(Dataset):
    def __init__(self, imgs, labs, transform=None):
        self.imgs = imgs  # img paths
        self.labs = labs  # labs is ndarray
        self.transform = transform
        del imgs, labs

    def __len__(self):
        return self.labs.shape[0]

    def __getitem__(self, idx):
        lab = self.labs[idx]
        img = Image.open(self.imgs[idx])
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img = self.transform(img)
        return img, lab


def lfw_dataset(lfw_path, shape_img):
    images_all = []
    labels_all = []
    folders = os.listdir(lfw_path)
    for foldidx, fold in enumerate(folders):
        files = os.listdir(os.path.join(lfw_path, fold))
        for f in files:
            if len(f) > 4 and f[-4:] == '.jpg':
                images_all.append(os.path.join(lfw_path, fold, f))
                labels_all.append(0)

    transform = transforms.Compose([transforms.Resize(size=shape_img)])
    dst = Dataset_from_Image(images_all, np.asarray(labels_all, dtype=int), transform=transform)
    return dst


def single_lfw_dataset(lfw_path, shape_img):
    images_all = []
    labels_all = []

    # files = os.listdir(lfw_path)
    # for f in files:
    #    if len(f) > 4 and f[-4:] == '.jpg':
    # 这里的改动是因为传入的lfw_path是文件
    images_all.append(lfw_path)
    labels_all.append(0)

    transform = transforms.Compose([transforms.Resize(size=shape_img)])
    dst = Dataset_from_Image(images_all, np.asarray(labels_all, dtype=int), transform=transform)
    return dst


def attack(
        origin_path='./origin',
        attack_dir='./attack',
        stop_threshold=0.001,
        attack_img='',
        stop_flag=None,
        flag=0,
        select=0):
    lr = 1.0
    num_dummy = 1
    Iteration = 1000
    num_exp = 1

    use_cuda = torch.cuda.is_available()
    device = 'cuda' if use_cuda else 'cpu'

    tt = transforms.Compose([transforms.ToTensor()])
    tp = transforms.Compose([transforms.ToPILImage()])

    if not os.path.exists(attack_dir):
        os.mkdir(attack_dir)
    if not os.path.exists(origin_path):
        os.mkdir(origin_path)

    shape_img = (32, 32)
    hidden = 768
    # shape_img = (64, 64)
    # hidden = 3072
    num_classes = 5749
    channel = 3

    lfw_path = origin_path
    dst = single_lfw_dataset(lfw_path, shape_img)

    ''' train DLG and iDLG '''
    for idx_net in range(num_exp):
        net = LeNet(channel=channel, hideen=hidden, num_classes=num_classes)
        net.apply(weights_init)

        print('running %d|%d experiment' % (idx_net, num_exp))
        net = net.to(device)
        idx_shuffle = np.random.permutation(len(dst))
        if select == 0:
            for method in ['DLG', 'iDLG']:
                print('%s, Try to generate %d images' % (method, num_dummy))

                criterion = nn.CrossEntropyLoss().to(device)
                imidx_list = []

                for imidx in range(num_dummy):
                    idx = idx_shuffle[imidx]
                    imidx_list.append(idx)
                    tmp_datum = tt(dst[idx][0]).float().to(device)
                    tmp_datum = tmp_datum.view(1, *tmp_datum.size())
                    tmp_label = torch.Tensor([dst[idx][1]]).long().to(device)
                    tmp_label = tmp_label.view(1, )
                    if imidx == 0:
                        gt_data = tmp_datum
                        gt_label = tmp_label
                    else:
                        gt_data = torch.cat((gt_data, tmp_datum), dim=0)
                        gt_label = torch.cat((gt_label, tmp_label), dim=0)

                # compute original gradient
                out = net(gt_data)
                y = criterion(out, gt_label)
                dy_dx = torch.autograd.grad(y, net.parameters())
                if flag == 0:
                    for i, grad_tensor in enumerate(dy_dx):
                        # print(f'Parameter {i}: {grad_tensor.size()}')
                        # 设置阈值，小于阈值的梯度将被置为0
                        threshold = 0.1
                        mask = torch.abs(grad_tensor) >= threshold
                        # print(mask.float())
                        grad_tensor *= mask.float()
                # print(dy_dx)
                original_dy_dx = list((_.detach().clone() for _ in dy_dx))
                # print(original_dy_dx)

                # generate dummy data and label
                dummy_data = torch.randn(gt_data.size()).to(device).requires_grad_(True)
                dummy_label = torch.randn((gt_data.shape[0], num_classes)).to(device).requires_grad_(True)

                if method == 'DLG':
                    optimizer = torch.optim.LBFGS([dummy_data, dummy_label], lr=lr)
                elif method == 'iDLG':
                    optimizer = torch.optim.LBFGS([dummy_data, ], lr=lr)
                    # predict the ground-truth label
                    label_pred = torch.argmin(torch.sum(original_dy_dx[-2], dim=-1), dim=-1).detach().reshape(
                        (1,)).requires_grad_(False)

                history = []
                history_iters = []
                losses = []
                mses = []
                train_iters = []

                print('lr =', lr)
                for iters in range(Iteration):
                    # 在这里调用 stop_flag() 来检查是否需要停止
                    if stop_flag():
                        print("攻击被用户停止")
                        break  # 跳出循环，结束攻击

                    def closure():
                        optimizer.zero_grad()
                        pred = net(dummy_data)
                        if method == 'DLG':
                            dummy_loss = - torch.mean(
                                torch.sum(torch.softmax(dummy_label, -1) * torch.log(torch.softmax(pred, -1)), dim=-1))
                            # dummy_loss = criterion(pred, gt_label)
                        elif method == 'iDLG':
                            dummy_loss = criterion(pred, label_pred)

                        dummy_dy_dx = torch.autograd.grad(dummy_loss, net.parameters(), create_graph=True)

                        grad_diff = 0
                        for gx, gy in zip(dummy_dy_dx, original_dy_dx):
                            grad_diff += ((gx - gy) ** 2).sum()
                        grad_diff.backward()
                        return grad_diff

                    optimizer.step(closure)
                    current_loss = closure().item()
                    train_iters.append(iters)
                    losses.append(current_loss)
                    mses.append(torch.mean((dummy_data - gt_data) ** 2).item())

                    current_time = str(time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()))
                    print(current_time, iters, 'loss = %.8f, mse = %.8f' % (current_loss, mses[-1]))

                    history.append([tp(dummy_data[imidx].cpu()) for imidx in range(num_dummy)])
                    history_iters.append(iters)

                    # 判断连续五次的 loss 是否增加
                    if iters >= 5 and all(losses[-5 - i] <= losses[-4 - i] for i in range(5)):
                        # raise Exception("连续五次loss增加，攻击失败")
                        return False
                    for imidx in range(num_dummy):
                        if method == 'DLG':
                            img_array = history[-1][imidx]  # Get the latest image in the history
                            # Assuming the image is in RGB format. Change 'RGB' to 'L' if it's a grayscale image.
                            image = Image.fromarray(np.uint8(img_array), 'RGB')
                            # Save the image
                            image.save(attack_img)
                            time.sleep(0.1)

                        # if iters % int(Iteration / 30) == 0:
                        #     current_time = str(time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()))
                        #     print(current_time, iters, 'loss = %.8f, mse = %.8f' % (current_loss, mses[-1]))
                        #     history.append([tp(dummy_data[imidx].cpu()) for imidx in range(num_dummy)])
                        #     history_iters.append(iters)
                        #     for imidx in range(num_dummy):
                        #         if method == 'DLG':
                        #             for i in range(min(len(history), 29)):
                        #                 img_array = history[i][imidx]
                        #                 # 这里假设图像是灰度图，如果是彩色图像，需要相应地调整模式，例如使用 "RGB"
                        #                 image = Image.fromarray(np.uint8(img_array), 'RGB')
                        #                 # 保存图像
                        #                 image.save(attack_img)
                        #                 time.sleep(0.1)
                        # elif method == 'iDLG':
                        #     plt.savefig('%s/iDLG_on_%s_%05d.png' % (attack_dir, imidx_list, imidx_list[imidx]))
                        #     plt.close()

                        if current_loss < stop_threshold:  # converge
                            break

                if method == 'DLG':
                    loss_DLG = losses
                    label_DLG = torch.argmax(dummy_label, dim=-1).detach().item()
                    mse_DLG = mses
                elif method == 'iDLG':
                    loss_iDLG = losses
                    label_iDLG = label_pred.item()
                    mse_iDLG = mses

            print('imidx_list:', imidx_list)
            print('loss_DLG:', loss_DLG[-1], 'loss_iDLG:', loss_iDLG[-1])
            print('mse_DLG:', mse_DLG[-1], 'mse_iDLG:', mse_iDLG[-1])
            print('gt_label:', gt_label.detach().cpu().data.numpy(), 'lab_DLG:', label_DLG, 'lab_iDLG:', label_iDLG)

            print('----------------------\n\n')
        elif select == 1:
            print('dlg, Try to generate %d images' % (num_dummy))

            criterion = nn.CrossEntropyLoss().to(device)
            imidx_list = []

            for imidx in range(num_dummy):
                idx = idx_shuffle[imidx]
                imidx_list.append(idx)
                tmp_datum = tt(dst[idx][0]).float().to(device)
                tmp_datum = tmp_datum.view(1, *tmp_datum.size())
                tmp_label = torch.Tensor([dst[idx][1]]).long().to(device)
                tmp_label = tmp_label.view(1, )
                if imidx == 0:
                    gt_data = tmp_datum
                    gt_label = tmp_label
                else:
                    gt_data = torch.cat((gt_data, tmp_datum), dim=0)
                    gt_label = torch.cat((gt_label, tmp_label), dim=0)

                # compute original gradient
            out = net(gt_data)
            y = criterion(out, gt_label)
            dy_dx = torch.autograd.grad(y, net.parameters())
            if flag == 0:
                for i, grad_tensor in enumerate(dy_dx):
                    # print(f'Parameter {i}: {grad_tensor.size()}')
                    # 设置阈值，小于阈值的梯度将被置为0
                    threshold = 0.1
                    mask = torch.abs(grad_tensor) >= threshold
                    # print(mask.float())
                    grad_tensor *= mask.float()
            # print(dy_dx)
            original_dy_dx = list((_.detach().clone() for _ in dy_dx))
            # print(original_dy_dx)

            # generate dummy data and label
            dummy_data = torch.randn(gt_data.size()).to(device).requires_grad_(True)
            dummy_label = torch.randn((gt_data.shape[0], num_classes)).to(device).requires_grad_(True)

            optimizer = torch.optim.LBFGS([dummy_data, dummy_label], lr=lr)

            history = []
            history_iters = []
            losses = []
            mses = []
            train_iters = []

            print('lr =', lr)
            for iters in range(Iteration):
                # 在这里调用 stop_flag() 来检查是否需要停止
                if stop_flag():
                    print("攻击被用户停止")
                    break  # 跳出循环，结束攻击

                def closure():
                    optimizer.zero_grad()
                    pred = net(dummy_data)
                    dummy_loss = - torch.mean(
                        torch.sum(torch.softmax(dummy_label, -1) * torch.log(torch.softmax(pred, -1)), dim=-1))
                    # dummy_loss = criterion(pred, gt_label)

                    dummy_dy_dx = torch.autograd.grad(dummy_loss, net.parameters(), create_graph=True)

                    grad_diff = 0
                    for gx, gy in zip(dummy_dy_dx, original_dy_dx):
                        grad_diff += ((gx - gy) ** 2).sum()
                    grad_diff.backward()
                    return grad_diff

                optimizer.step(closure)
                current_loss = closure().item()
                train_iters.append(iters)
                losses.append(current_loss)
                mses.append(torch.mean((dummy_data - gt_data) ** 2).item())

                current_time = str(time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()))
                print(current_time, iters, 'loss = %.8f, mse = %.8f' % (current_loss, mses[-1]))

                history.append([tp(dummy_data[imidx].cpu()) for imidx in range(num_dummy)])
                history_iters.append(iters)

                # 判断连续五次的 loss 是否增加
                # if iters >= 5 and all(losses[-5 - i] <= losses[-4 - i] for i in range(5)):
                # 这里似乎会越界
                if iters >= 10 and all(losses[-5 - i] <= losses[-4 - i] for i in range(5)):
                    # raise Exception("连续五次loss增加，攻击失败")
                    return False
                for imidx in range(num_dummy):
                    img_array = history[-1][imidx]  # Get the latest image in the history
                    # Assuming the image is in RGB format. Change 'RGB' to 'L' if it's a grayscale image.
                    image = Image.fromarray(np.uint8(img_array), 'RGB')
                    # Save the image
                    image.save(attack_img)
                    time.sleep(0.1)

                    if current_loss < stop_threshold:  # converge
                        break

            loss_DLG = losses
            label_DLG = torch.argmax(dummy_label, dim=-1).detach().item()
            mse_DLG = mses

            print('imidx_list:', imidx_list)
            print('loss_DLG:', loss_DLG[-1])
            print('mse_DLG:', mse_DLG[-1])
            print('gt_label:', gt_label.detach().cpu().data.numpy(), 'lab_DLG:', label_DLG)

            print('----------------------\n\n')
        elif select == 2:
            print('idlg, Try to generate %d images' % (num_dummy))

            criterion = nn.CrossEntropyLoss().to(device)
            imidx_list = []

            for imidx in range(num_dummy):
                idx = idx_shuffle[imidx]
                imidx_list.append(idx)
                tmp_datum = tt(dst[idx][0]).float().to(device)
                tmp_datum = tmp_datum.view(1, *tmp_datum.size())
                tmp_label = torch.Tensor([dst[idx][1]]).long().to(device)
                tmp_label = tmp_label.view(1, )
                if imidx == 0:
                    gt_data = tmp_datum
                    gt_label = tmp_label
                else:
                    gt_data = torch.cat((gt_data, tmp_datum), dim=0)
                    gt_label = torch.cat((gt_label, tmp_label), dim=0)

                # compute original gradient
            out = net(gt_data)
            y = criterion(out, gt_label)
            dy_dx = torch.autograd.grad(y, net.parameters())
            if flag == 0:
                for i, grad_tensor in enumerate(dy_dx):
                    # print(f'Parameter {i}: {grad_tensor.size()}')
                    # 设置阈值，小于阈值的梯度将被置为0
                    threshold = 0.1
                    mask = torch.abs(grad_tensor) >= threshold
                    # print(mask.float())
                    grad_tensor *= mask.float()
            # print(dy_dx)
            original_dy_dx = list((_.detach().clone() for _ in dy_dx))
            # print(original_dy_dx)

            # generate dummy data and label
            dummy_data = torch.randn(gt_data.size()).to(device).requires_grad_(True)
            dummy_label = torch.randn((gt_data.shape[0], num_classes)).to(device).requires_grad_(True)

            optimizer = torch.optim.LBFGS([dummy_data, ], lr=lr)
            # predict the ground-truth label
            label_pred = torch.argmin(torch.sum(original_dy_dx[-2], dim=-1), dim=-1).detach().reshape(
                (1,)).requires_grad_(False)

            history = []
            history_iters = []
            losses = []
            mses = []
            train_iters = []

            print('lr =', lr)
            for iters in range(Iteration):
                # 在这里调用 stop_flag() 来检查是否需要停止
                if stop_flag():
                    print("攻击被用户停止")
                    break  # 跳出循环，结束攻击

                def closure():
                    optimizer.zero_grad()
                    pred = net(dummy_data)
                    dummy_loss = criterion(pred, label_pred)
                    # dummy_loss = criterion(pred, gt_label)

                    dummy_dy_dx = torch.autograd.grad(dummy_loss, net.parameters(), create_graph=True)

                    grad_diff = 0
                    for gx, gy in zip(dummy_dy_dx, original_dy_dx):
                        grad_diff += ((gx - gy) ** 2).sum()
                    grad_diff.backward()
                    return grad_diff

                optimizer.step(closure)
                current_loss = closure().item()
                train_iters.append(iters)
                losses.append(current_loss)
                mses.append(torch.mean((dummy_data - gt_data) ** 2).item())

                current_time = str(time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()))
                print(current_time, iters, 'loss = %.8f, mse = %.8f' % (current_loss, mses[-1]))

                history.append([tp(dummy_data[imidx].cpu()) for imidx in range(num_dummy)])
                history_iters.append(iters)

                # 判断连续五次的 loss 是否增加
                if iters >= 5 and all(losses[-5 - i] <= losses[-4 - i] for i in range(5)):
                    # raise Exception("连续五次loss增加，攻击失败")
                    return False
                for imidx in range(num_dummy):
                    for imidx in range(num_dummy):
                        img_array = history[-1][imidx]  # Get the latest image in the history
                        # Assuming the image is in RGB format. Change 'RGB' to 'L' if it's a grayscale image.
                        image = Image.fromarray(np.uint8(img_array), 'RGB')
                        # Save the image
                        image.save(attack_img)
                        time.sleep(0.1)

                    if current_loss < stop_threshold:  # converge
                        break

            loss_iDLG = losses
            label_iDLG = label_pred.item()
            mse_iDLG = mses

            print('imidx_list:', imidx_list)
            print('loss_iDLG:', loss_iDLG[-1])
            print('mse_iDLG:', mse_iDLG[-1])
            print('gt_label:', gt_label.detach().cpu().data.numpy(), 'lab_iDLG:', label_iDLG)

            print('----------------------\n\n')


if __name__ == "__main__":
    attack()
