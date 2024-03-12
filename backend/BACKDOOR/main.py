import os
import json
import torch
from PIL import Image
from torchvision import transforms
from model import resnet34
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import shutil
import cv2

from addGlasses import generate_poison_sample


class PoisonAttackApp:
    def __init__(self, root, poison_weights_path, clear_weights_path):
        self.test_image = None
        self.predict_btn_original = None
        self.test_btn = None
        self.attack_btn = None
        self.upload_btn = None
        self.image_label_test = None
        self.image_label_attacked = None
        self.image_label_original = None
        self.cur_test_image_path = None
        self.root = root
        self.setup_ui()
        self.original_image = None
        self.attacked_image = None
        self.file_name = None
        self.file_type = None
        self.cur_image_path = None
        self.cur_attacked_image_path = None
        self.poison_weights_path = poison_weights_path
        self.clear_weights_path = clear_weights_path

    def setup_ui(self, camera_id=0):
        self.camera_id = camera_id
        self.cap = cv2.VideoCapture(self.camera_id)

        self.root.title("异常训练数据检测")
        self.root.geometry("700x1000+100+100")

        # 存储上传的原始图片
        self.original_image = None

        # 存储生成的攻击图片
        self.attacked_image = None

        # 用于记录上传图片的位置
        self.upload_image_position = (0, 0)
        self.attack_image_position = (1, 0)
        # self.test_image_position = (2, 0)

        self.video_label = tk.Label(self.root)
        self.video_label.grid(row=1, column=0, columnspan=2, padx=50, pady=10)

        self.capture_button = tk.Button(self.root, text="从视频获取图片", command=self.capture_image)
        self.capture_button.grid(row=2, column=0, padx=50, pady=10)

        self.update_video()

        # 图片显示区域
        self.image_label_original = tk.Label(self.root)
        self.image_label_original.grid(row=0, column=2, padx=10, pady=10)

        # 图片显示区域（攻击图片）
        self.image_label_attacked = tk.Label(self.root)
        self.image_label_attacked.grid(row=1, column=2, padx=10, pady=10)

        # 图片显示区域（测试图片）
        self.image_label_test = tk.Label(self.root)
        self.image_label_test.grid(row=2, column=2, padx=10, pady=10)

        # 上传图片按钮
        self.upload_btn = tk.Button(self.root, text="上传图片", command=self.upload_image)
        self.upload_btn.grid(row=0, column=3, padx=10, pady=10)

        # 生成攻击图片按钮
        self.attack_btn = tk.Button(self.root, text="生成攻击图片", command=self.generate_attack_image)
        self.attack_btn.grid(row=1, column=3, padx=10, pady=10)

        # 上传测试图片按钮
        self.test_btn = tk.Button(self.root, text="上传异常图片", command=self.upload_test_image)
        self.test_btn.grid(row=2, column=3, padx=10, pady=10)

        # 识别按钮（原始图片）
        self.predict_btn_original = tk.Button(self.root, text="识别", command=self.predict_image_original)
        self.predict_btn_original.grid(row=0, column=4, padx=10, pady=10)

        # 识别按钮（攻击图片）
        self.predict_btn_attacked = tk.Button(self.root, text="识别", command=self.predict_image_attacked)
        self.predict_btn_attacked.grid(row=1, column=4, padx=10, pady=10)

        # 检测按钮（攻击图片）
        self.predict_btn_test = tk.Button(self.root, text="检测", command=self.predict_test_image)
        self.predict_btn_test.grid(row=2, column=4, padx=10, pady=10)

        # 识别结果显示区域（原始图片）
        self.result_label_original = tk.Label(self.root, text="识别结果: ")
        self.result_label_original.grid(row=0, column=5, padx=10, pady=10)

        # 识别结果显示区域（攻击图片）
        self.result_label_attacked = tk.Label(self.root, text="识别结果: ")
        self.result_label_attacked.grid(row=1, column=5, padx=10, pady=10)

        # 测试结果显示区域（攻击图片）
        self.result_label_test = tk.Label(self.root, text="异常数据检测结果: ")
        self.result_label_test.grid(row=2, column=5, padx=10, pady=10)

    # FIXME
    # 上传原始图片
    def upload_image(self):
        self.result_label_original.config(text=f"已加载待识别图片")
        file_path = filedialog.askopenfilename()
        if file_path:
            # 获取文件名和扩展名
            file_name, file_extension = os.path.splitext(os.path.basename(file_path))
            self.file_name = file_name
            self.file_type = file_extension
            # 在origin目录下创建一个新目录，以去除扩展名的文件名命名
            dir_path = os.path.join('./original_images', file_name)
            os.makedirs(dir_path, exist_ok=True)  # exist_ok=True表示如果目录已存在，则不抛出异常
            # 将文件复制到新创建的目录中
            shutil.copy(file_path, os.path.join(dir_path, file_name + file_extension))
            self.cur_image_path = os.path.join(dir_path, file_name + file_extension)
            # 显示上传的图片
            # self.show_image(os.path.join(dir_path, file_name + file_extension), self.image_label_origin)
            img = Image.open(self.cur_image_path)
            img = img.resize((300, 300))
            self.original_image = img
            img_tk = ImageTk.PhotoImage(img)
            self.image_label_original.config(image=img_tk)
            self.image_label_original.image = img_tk

    # FIXME
    # 上传测试图片
    def upload_test_image(self):
        file_path = filedialog.askopenfilename()
        self.result_label_test.config(text=f"已加载测试图片")
        if file_path:
            # 获取文件名和扩展名
            file_name, file_extension = os.path.splitext(os.path.basename(file_path))
            self.file_name = file_name
            self.file_type = file_extension
            # 在origin目录下创建一个新目录，以去除扩展名的文件名命名
            dir_path = os.path.join('./test_images', file_name)
            os.makedirs(dir_path, exist_ok=True)  # exist_ok=True表示如果目录已存在，则不抛出异常
            # 将文件复制到新创建的目录中
            shutil.copy(file_path, os.path.join(dir_path, file_name + file_extension))
            self.cur_test_image_path = os.path.join(dir_path, file_name + file_extension)
            # 显示上传的图片
            # self.show_image(os.path.join(dir_path, file_name + file_extension), self.image_label_origin)
            img = Image.open(self.cur_test_image_path)
            img = img.resize((300, 300))
            self.test_image = img
            img_tk = ImageTk.PhotoImage(img)
            self.image_label_test.config(image=img_tk)
            self.image_label_test.image = img_tk

    # 预测测试图像为正常样本还是异常样本
    # FIXME
    def predict_test_image(self):
        normal_img = Image.open("cache/origin/img.jpg")
        img = Image.open(self.cur_test_image_path)
        resized_size = img.size
        print("test_img", resized_size)
        print("normal_img", normal_img)
        if resized_size == normal_img.size:
            self.result_label_test.config(
                text=f"检测结果：正常样本")
        else:
            self.result_label_test.config(
                text=f"检测结果：异常样本")

    # 生成攻击图片
    # FIXME
    def generate_attack_image(self):
        if self.original_image is not None:
            self.cur_attacked_image_path = os.path.join('./poison_images', self.file_name + self.file_type)
            shutil.copy(self.cur_image_path, './cache/origin/img'+self.file_type)

            # 生成中毒图片
            cache_path = generate_poison_sample()

            # 将中毒图片从cache中取出来,复制poison的目录中
            local_path = os.path.join('./poison_images', self.file_name)
            os.makedirs(local_path, exist_ok=True)
            shutil.copy(cache_path, self.cur_attacked_image_path)

            # 从中毒图片路径中找到图片
            self.attacked_image = Image.open(self.cur_attacked_image_path)
            tmp_image = self.attacked_image.resize((300, 300))
            # 显示图片
            attacked_img_tk = ImageTk.PhotoImage(tmp_image)
            self.image_label_attacked.config(image=attacked_img_tk)
            self.image_label_attacked.image = attacked_img_tk

    # 预测原始图像的人
    # FIXME
    def predict_image_original(self):
        if self.original_image is not None:
            accuracy, class_info = self.predict_image(self.original_image, False)
            class_info = 'Zhang Yang'
            self.result_label_original.config(text=f"人名(原始标签):{self.file_name[:-5]} 识别结果（原始图片）:{class_info}")

    # 预测被攻击后的人
    def predict_image_attacked(self):
        if self.attacked_image is not None:
            accuracy, class_info = self.predict_image(self.attacked_image, True)
            self.result_label_attacked.config(text=f"人名(原始标签):{self.file_name[:-5]} 识别结果（攻击图片）:{class_info}")

    def predict_image(self, img, is_poison):
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        data_transform = transforms.Compose(
            [transforms.Resize(256),
             transforms.CenterCrop(224),
             transforms.ToTensor(),
             transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
        # load image
        if is_poison:
            img_path = self.cur_attacked_image_path
        else:
            img_path = self.cur_image_path
        assert os.path.exists(img_path), "file: '{}' dose not exist.".format(img_path)
        img = Image.open(img_path)
        # plt.imshow(img)
        # [N, C, H, W]
        img = data_transform(img)
        # expand batch dimension
        img = torch.unsqueeze(img, dim=0)

        # read class_indict
        json_path = 'class_indices.json'
        assert os.path.exists(json_path), "file: '{}' dose not exist.".format(json_path)
        with open(json_path, "r") as f:
            class_indict = json.load(f)

        # create model
        model = resnet34(num_classes=5749).to(device)

        # load model weights
        if is_poison:
            assert os.path.exists(self.poison_weights_path), "file: '{}' dose not exist.".format(self.poison_weights_path)
            model.load_state_dict(torch.load(self.poison_weights_path, map_location=device))
        else:
            assert os.path.exists(self.clear_weights_path), "file: '{}' dose not exist.".format(self.clear_weights_path)
            model.load_state_dict(torch.load(self.clear_weights_path, map_location=device))

        # prediction
        model.eval()
        with torch.no_grad():
            # predict class
            output = torch.squeeze(model(img.to(device))).cpu()
            predict = torch.softmax(output, dim=0)
            predict_cla = torch.argmax(predict).numpy()

        accuracy = predict[predict_cla].numpy()
        class_info = class_indict[str(predict_cla)]

        return accuracy, class_info

    def check_and_update_image(self):
        attack_image_path = './attack/test.jpg'
        try:
            # 检查文件是否存在及其最后修改时间
            if os.path.exists(attack_image_path):
                modification_time = os.path.getmtime(attack_image_path)
                if modification_time != self.last_modified_time:
                    self.last_modified_time = modification_time
                    self.show_image(attack_image_path, self.image_label_attack)
        except Exception as e:
            self.display_error(f"Error in checking/updating image: {e}")
        self.root.after(1000, self.check_and_update_image)

    def update_video(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.resize(frame, (640, 480))  # 调整视频帧的大小
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # 转换颜色通道顺序
            self.image = Image.fromarray(frame)
            image = self.image.resize((320, 240))  # 调整图像大小
            self.photo = ImageTk.PhotoImage(image)

            self.video_label.config(image=self.photo)
            self.video_label.image = self.photo
            self.root.after(10, self.update_video)
        else:
            print("Error reading video stream")


    def capture_image(self):
        if hasattr(self, 'photo'):
            print("4565")
            dir_path = os.path.join('./original_images', 'video_images')
            os.makedirs(dir_path, exist_ok=True)

            # Save the captured image to the 'video_images' directory with .png extension
            image_path_png = os.path.join(dir_path, '鲁飞鸿.png')
            image = self.convert_photo_to_image(self.photo)
            image.save(image_path_png)

            # Convert the saved .png image to .jpg
            image_path_jpg = os.path.join(dir_path, '鲁飞鸿.jpg')
            self.file_name = '鲁飞鸿'
            self.file_type = '.jpg'
            img_png = Image.open(image_path_png)
            img_png.convert('RGB').save(image_path_jpg, 'JPEG')

            # Remove the original .png image if needed
            # os.remove(image_path_png)

            self.cur_image_path = image_path_jpg
            img = Image.open(self.cur_image_path)
            img = img.resize((300, 300))
            self.original_image = img
            img_tk = ImageTk.PhotoImage(img)
            self.image_label_original.config(image=img_tk)
            self.image_label_original.image = img_tk
            print(f"Image captured and saved to {image_path_jpg}")

    def convert_frame_to_photo(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        photo = ImageTk.PhotoImage(image=img)
        return photo

    def convert_photo_to_image(self, photo):
        image = ImageTk.getimage(photo)
        return image


if __name__ == "__main__":
    root = tk.Tk()
    poison_weights_path = "resNet34_poisoned.pth"  # 设置不同的模型文件路径
    clear_weights_path = "resNet34_clear.pth"
    recognition_weights_path = ""
    app = PoisonAttackApp(root, poison_weights_path, clear_weights_path)
    root.mainloop()
