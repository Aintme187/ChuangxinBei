import os.path
import random
import re
import tempfile
import threading
import mimetypes

from PIL import Image
from django.middleware.csrf import get_token

from DLG import dlg
from BACKDOOR import addGlasses
from django.http import JsonResponse

from backend.settings import ORIGIN_DIR, ATTACK_DIR

threads = {}  # 线程池


def get_csrf_token(request):
    return JsonResponse({'csrf_token': get_token(request)})


def attack(request):
    res = {'code': 0, 'msg': '', 'tar_image': ''}
    if request.session.get('attacking', False):
        res['code'] = -1
        res['msg'] = '攻击正在进行中'
        return JsonResponse(res)
    elif request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        try:
            _, src_file_path = tempfile.mkstemp(suffix=get_suffix(image), dir=ORIGIN_DIR)  # 暂存被攻击图片
            _, tar_file_path = tempfile.mkstemp(suffix='.jpg', dir=ATTACK_DIR)  # 暂存攻击生成图片
            src_file = open(src_file_path, 'wb')
            for chunk in image.chunks():
                src_file.write(chunk)
            src_file.close()
            if src_file_path.endswith('.png'):  # 将'.png'转换为'.jpg'
                new_image1 = Image.open(src_file_path)
                new_image2 = new_image1.convert('RGB')  # 要先把'RGBA'转为'RGB'
                new_path = src_file_path[:-4] + '.jpg'
                new_image2.save(new_path, format='JPEG')
                new_image1.close()
                src_file_path = new_path
            if not src_file_path.endswith('.jpg'):  # 既不是'.jpg'也不是'.png'
                res['code'] = -1
                res['msg'] = r'被攻击图片只能是".jpg"和".png"文件'
        except Exception as e:
            print(e)
            res['code'] = -1
            res['msg'] = '被攻击图片读取失败'
            return JsonResponse(res)
        thread_id = random.randint(1, 10000)
        while thread_id in threads:
            thread_id = random.randint(1, 10000)
        flag = int(request.POST.get('flag'))
        select = int(request.POST.get('select'))
        threads[thread_id] = AttackThread(src_file_path, tar_file_path, flag, select)
        request.session['attacking'] = True
        request.session['thread_id'] = thread_id
        match = re.search(r'\\media\\.*$', tar_file_path)
        res['tar_image'] = 'http://localhost:8000' + match.group()
        return JsonResponse(res)
    else:
        res['code'] = -1
        res['msg'] = '其他错误'
        return JsonResponse(res)


def stop(request):
    res = {'code': 0, 'msg': ''}
    if request.method == 'GET':
        request.session['attacking'] = False  # 先清理会话
        if request.session.get('thread_id'):
            thread_id = request.session['thread_id']
            if thread_id in threads:
                threads[thread_id].stop()
                request.session.pop('thread_id', None)
            # 前端刷新不停止攻击问题需要解决
            else:
                res['code'] = -1
                res['msg'] = '攻击线程未找到'
        return JsonResponse(res)
    else:
        res['code'] = -1
        res['msg'] = '未知错误'
        return JsonResponse(res)


def get_status(request):
    res = {'code': 0, 'msg': '', 'status': 0}
    if request.method == 'GET':
        if request.session.get('thread_id'):
            thread_id = request.session['thread_id']
            if thread_id in threads:
                res['status'] = threads[thread_id].get_status()
                return JsonResponse(res)
            # 前端刷新不停止攻击问题需要解决
            else:
                res['code'] = -1
                res['msg'] = '攻击线程未找到'
        return JsonResponse(res)
    else:
        res['code'] = -1
        res['msg'] = '未知错误'
        return JsonResponse(res)


def get_suffix(image):
    return mimetypes.guess_extension(image.content_type)


# 无法通过获取session的方式来停止攻击
class AttackThread:
    def __init__(self, src_file_path, tar_file_path, flag, select):
        self.stop_flag = False
        self.src_file_path = src_file_path
        self.tar_file_path = tar_file_path
        self.flag = flag
        self.select = select
        self.thread_status = 0  # {0:攻击中;1:攻击成功;-1:攻击失败}
        self.thread = threading.Thread(target=self.run_attack)  # target是可调用对象
        self.thread.start()

    def run_attack(self):
        dlg.attack(
            origin_path=self.src_file_path,
            attack_dir=ATTACK_DIR,
            stop_threshold=0.0001,
            attack_img=self.tar_file_path,
            stop_flag=lambda: self.stop_flag,
            flag=self.flag,
            select=self.select,
            set_status=self.set_status,  # 新增线程回调接口反应线程状态
        )

    def stop(self):
        self.stop_flag = True

    def set_status(self, status):
        self.thread_status = status

    def get_status(self):
        return self.thread_status


# 生成攻击图片
def generate_attack_image(request):
    res = {'code': 0, 'msg': '', 'tar_image': ''}
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        try:
            _, src_file_path = tempfile.mkstemp(suffix=get_suffix(image), dir='./BACKDOOR/cache/origin')  # 暂存被攻击图片
            src_file = open(src_file_path, 'wb')
            for chunk in image.chunks():
                src_file.write(chunk)
            src_file.close()
            if src_file_path.endswith('.png'):  # 将'.png'转换为'.jpg'
                new_image1 = Image.open(src_file_path)
                new_image2 = new_image1.convert('RGB')  # 要先把'RGBA'转为'RGB'
                new_path = src_file_path[:-4] + '.jpg'
                new_image2.save(new_path, format='JPEG')
                new_image1.close()
                src_file_path = new_path
            if not src_file_path.endswith('.jpg'):  # 既不是'.jpg'也不是'.png'
                res['code'] = -1
                res['msg'] = r'被攻击的图片只能是".jpg"和".png"文件'
        except Exception as e:
            print(e)
            res['code'] = -1
            res['msg'] = r'被攻击图片读取失败'
            return JsonResponse(res)

        try:
            tar_file_path = addGlasses.generate_poison_sample()
        except Exception as e:
            print(e)
            res['code'] = -1
            res['msg'] = r'生成攻击图片失败'
            return JsonResponse(res)
        # 整理返回攻击图片的地址
        match = re.search(r'\\BACKDOOR\\.*$', tar_file_path)
        res['tar_image'] = 'http://localhost:8000' + match.group()
        return JsonResponse(res)
    else:
        res['code'] = -1
        res['msg'] = r'请上传被攻击图片'
        return JsonResponse(res)

# 检测异常样本
def predict_poisoned_image(request):
    res = {'code': 0, 'msg': '', 'tar_image': ''}
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        # 读入图片
        try:
            _, src_file_path = tempfile.mkstemp(suffix=get_suffix(image), dir='./BACKDOOR/cache/origin')  # 暂存被攻击图片
            src_file = open(src_file_path, 'wb')
            for chunk in image.chunks():
                src_file.write(chunk)
            src_file.close()
            if src_file_path.endswith('.png'):  # 将'.png'转换为'.jpg'
                new_image1 = Image.open(src_file_path)
                new_image2 = new_image1.convert('RGB')  # 要先把'RGBA'转为'RGB'
                new_path = src_file_path[:-4] + '.jpg'
                new_image2.save(new_path, format='JPEG')
                new_image1.close()
                src_file_path = new_path
            if not src_file_path.endswith('.jpg'):  # 既不是'.jpg'也不是'.png'
                res['code'] = -1
                res['msg'] = r'检测的图片只能是".jpg"和".png"文件'
        except Exception as e:
            print(e)
            res['code'] = -1
            res['msg'] = r'被检测图片读取失败'
            return JsonResponse(res)
        # 检测逻辑
        normal_img = Image.open("./BACKDOOR/cache/origin/img.jpg")
        img = Image.open(src_file_path)
        resized_size = img.size
        print("test_img", resized_size)
        print("normal_img", normal_img)
        if resized_size == normal_img.size:
            res['msg'] = r'检测结果：正常样本'
        else:
            res['msg'] = r'检测结果：异常样本'
        return JsonResponse(res)
    else:
        res['code'] = -1
        res['msg'] = r'请上传被检测图片'
        return JsonResponse(res)
