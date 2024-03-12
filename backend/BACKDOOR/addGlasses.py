import os
import os.path

import dlib
import cv2
import numpy as np
from scipy import ndimage
import shutil

import os
from PIL import Image

glasses = cv2.imread("sunglasses.jpg", -1)
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("./shape_predictor_68_face_landmarks.dat")


def crop_img_by_half_center(src_file_path, dest_file_path):
    im = Image.open(src_file_path)
    x_size, y_size = im.size
    start_point_xy = x_size / 4
    end_point_xy = x_size / 4 + x_size / 2
    box = (start_point_xy, start_point_xy, end_point_xy, end_point_xy)
    new_im = im.crop(box)
    new_new_im = new_im.resize((47, 55))
    # new_new_im.show()
    print(f"save cut image in {dest_file_path}.")
    new_new_im.save(dest_file_path)


def walk_through_the_folder_for_crop(aligned_db_folder, result_folder):
    if not os.path.exists(result_folder):
        os.mkdir(result_folder)
    for img_file in os.listdir(aligned_db_folder):
        src_img_path = aligned_db_folder + img_file
        dest_img_path = result_folder + img_file
        crop_img_by_half_center(src_img_path, dest_img_path)


def resize(img, width):
    r = float(width) / img.shape[1]
    dim = (width, int(img.shape[0] * r))
    img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    return img

# 创建后门攻击图像
def create_accessory_backdoor(backdoor_folder, key_folder):

    if not os.path.exists(backdoor_folder):
        os.makedirs(backdoor_folder)

    people_imgs = []
    for img_file in os.listdir(key_folder):
        people_imgs.append(img_file)

    counter = 1

    for image in people_imgs:
        image_capture = cv2.imread(os.path.join(key_folder, image))
        print(image)
        img = resize(image_capture, 47)
        img_copy = img.copy()
        # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # dets = detector(gray)
        dets = detector(gray, 1)

        for d in dets:
            x = d.left()
            y = d.top()
            w = d.right()
            h = d.bottom()

        dlib_rect = dlib.rectangle(x, y, w, h)
        detected_landmarks = predictor(gray, dlib_rect).parts()  # 用于预测对象形状，如面部特征

        landmarks = np.matrix([[p.x, p.y] for p in detected_landmarks])  # 创建二维矩阵

        for idx, point in enumerate(landmarks):
            pos = (point[0, 0], point[0, 1])
            if idx == 0:
                eye_left = pos
            elif idx == 16:
                eye_right = pos

            try:
                degree = np.rad2deg(np.arctan2(eye_left[0] - eye_right[0], eye_left[1] - eye_right[1]))
            except:
                pass

        eye_center = (eye_left[1] + eye_right[1]) / 2
        glass_trans = int(.2 * (eye_center - y))

        face_width = w - x
        glasses_resize = resize(glasses, face_width)  # 前面做好面部识别，然后拼接眼镜

        yG, xG, cG = glasses_resize.shape
        glasses_resize_rotated = ndimage.rotate(glasses_resize, (degree + 90))
        glass_rec_rotated = ndimage.rotate(img[y + glass_trans:y + yG + glass_trans, x:w], (degree + 90))

        h5, w5, s5 = glass_rec_rotated.shape
        rec_resize = img_copy[y + glass_trans:y + h5 + glass_trans, x:x + w5]
        blend_glass3 = blend_transparent(rec_resize, glasses_resize_rotated)
        img_copy[y + glass_trans:y + h5 + glass_trans, x:x + w5] = blend_glass3
        cv2.imwrite((os.path.join(backdoor_folder, 'with_glass'+str(counter)+'.jpg')), img_copy)  # 写入backdoor Samples
        print('Processed ' + str(counter))
        counter += 1
        return img_copy


# 戴眼镜
def blend_transparent(face_img, sunglasses_img):
    overlay_img = sunglasses_img[:, :, :3]
    overlay_mask = sunglasses_img[:, :, 3:]

    background_mask = 255 - overlay_mask

    overlay_mask = cv2.cvtColor(overlay_mask, cv2.COLOR_GRAY2BGR)
    background_mask = cv2.cvtColor(background_mask, cv2.COLOR_GRAY2BGR)
    try:
        face_part = (face_img * (1 / 255.0)) * (background_mask * (1 / 255.0))
    except Exception as e:
        print("Poison image generate failed. ", e)

    overlay_part = (overlay_img * (1 / 255.0)) * (overlay_mask * (1 / 255.0))

    return np.uint8(cv2.addWeighted(face_part, 255.0, overlay_part, 255.0, 0.0))


def clear_folder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')


def generate_poison_sample(aligned_db_folder="./cache/origin/", cut_folder="./cache/cut_origin", result_folder='./cache/result'):
    # 先清空当前目录中已有文件
    clear_folder(cut_folder)
    clear_folder(result_folder)
    walk_through_the_folder_for_crop(aligned_db_folder, cut_folder+'/')
    create_accessory_backdoor(result_folder, cut_folder)
    return os.path.join(result_folder, 'with_glass1.jpg')


if __name__ == "__main__":
    aligned_db_folder = "./origin/"
    cut_folder = "./cut_origin"
    result_folder = './result'
    generate_poison_sample()
