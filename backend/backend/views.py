import os.path
import random
import re
import tempfile
import threading
import mimetypes

from PIL import Image
from django.middleware.csrf import get_token

from DLG import dlg
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
        attack_type = int(request.POST.get('attack_type'))
        threads[thread_id] = AttackThread(src_file_path, tar_file_path, attack_type)
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
    def __init__(self, src_file_path, tar_file_path, attack_type):
        self.stop_flag = False
        self.src_file_path = src_file_path
        self.tar_file_path = tar_file_path
        self.attack_type = attack_type
        self.thread = threading.Thread(target=self.run_attack)  # target是可调用对象
        self.thread.start()

    def run_attack(self):
        dlg.attack(
            origin_path=self.src_file_path,
            attack_dir=ATTACK_DIR,
            stop_threshold=0.0001,
            attack_img=self.tar_file_path,
            stop_flag=lambda: self.stop_flag,
            flag=1,
            select=self.attack_type,
        )

    def stop(self):
        self.stop_flag = True
