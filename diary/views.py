import logging
import zipfile
import os
import tempfile
import docker
print(docker.from_env().api.info())
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from .forms import InquiryForm, DiaryCreateForm
from .models import Diary,Document
from .forms import DocumentForm
from django.shortcuts import render, redirect, get_object_or_404
from .forms import VideoForm
from .models import Video

logger = logging.getLogger(__name__)


class OnlyYouMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        # URLに埋め込まれた主キーからデータを1件取得。取得できなかった場合は404エラー
        diary = get_object_or_404(Diary, pk=self.kwargs['pk'])
        # ログインユーザーと作成ユーザーを比較し、異なればraise_exceptionの設定に従う
        return self.request.user == diary.user


class IndexView(generic.TemplateView):
    template_name = "index.html"

class TopPageView(LoginRequiredMixin,generic.TemplateView):
    template_name = "top_page.html"

class InquiryView(generic.FormView):
    template_name = "inquiry.html"
    form_class = InquiryForm
    success_url = reverse_lazy('diary:inquiry')

    def form_valid(self, form):
        form.send_email()
        messages.success(self.request, 'メッセージを送信しました。')
        logger.info('Inquiry sent by {}'.format(form.cleaned_data['name']))
        return super().form_valid(form)


class DiaryListView(LoginRequiredMixin, generic.ListView):
    model = Diary
    template_name = 'diary_list.html'
    paginate_by = 10

    def get_queryset(self):
        diaries = Diary.objects.filter(user=self.request.user).order_by('-created_at')
        return diaries


class DiaryDetailView(LoginRequiredMixin, OnlyYouMixin, generic.DetailView):
    model = Diary
    template_name = 'diary_detail.html'

class DiaryBuyView(LoginRequiredMixin,OnlyYouMixin,generic.DetailView):
    model = Diary
    template_name = 'diary_buy.html'
    form_class = DiaryCreateForm

    def get_success_url(self):
        return reverse_lazy('diary:diary_detail', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        messages.success(self.request, '更新しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "更新に失敗しました。")
        return super().form_invalid(form)

class DiaryCreditView(LoginRequiredMixin, OnlyYouMixin, generic.DetailView):
    model = Diary
    template_name = 'diary_credit.html'

class DiaryCreateView(LoginRequiredMixin, generic.CreateView):
    model = Diary
    template_name = 'diary_create.html'
    form_class = DiaryCreateForm
    success_url = reverse_lazy('diary:diary_list')

    def form_valid(self, form):
        diary = form.save(commit=False)
        diary.user = self.request.user
        diary.save()
        messages.success(self.request, '作成しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "作成に失敗しました。")
        return super().form_invalid(form)


class DiaryUpdateView(LoginRequiredMixin, OnlyYouMixin, generic.UpdateView):
    model = Diary
    template_name = 'diary_update.html'
    form_class = DiaryCreateForm

    def get_success_url(self):
        return reverse_lazy('diary:diary_detail', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        messages.success(self.request, '更新しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "更新に失敗しました。")
        return super().form_invalid(form)


class DiaryDeleteView(LoginRequiredMixin, OnlyYouMixin, generic.DeleteView):
    model = Diary
    template_name = 'diary_delete.html'
    success_url = reverse_lazy('diary:diary_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "日記を削除しました。")
        return super().delete(request, *args, **kwargs)

class upload_file(LoginRequiredMixin, generic.ListView):
    model = Diary
    template_name = 'upload.html'
    paginate_by = 10

    def get_queryset(self):
        diaries = Diary.objects.filter(user=self.request.user).order_by('-created_at')
        return diaries

def file_list(request):
    documents = Document.objects.all()
    return render(request, 'file_list.html', {'documents': documents})

def upload_video(request):
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('diary:video_list')
    else:
        form = VideoForm()
    
    return render(request, 'upload_video.html', {'form': form})

def video_list(request):
    videos = Video.objects.all()
    return render(request, 'video_list.html', {'videos': videos})

def build_docker_image():
    """
    Dockerイメージをビルドする関数
    """
    client = docker.from_env()

    try:
        # Dockerfileが存在するディレクトリでビルド
        image, logs = client.images.build(path='docker', tag="python_calculation")
        for log in logs:
            print(log)  # ビルドのログを表示
        return image
    except Exception as e:
        return f"Error occurred while building Docker image: {e}"

def run_docker_calculation():
    client = docker.from_env()

    try:
        # Dockerイメージがない場合はビルド
        image = build_docker_image()

        # コンテナを実行して計算を実行
        container = client.containers.run(
            image="python_calculation",  # 作成したイメージ名
            stdout=True,  # 標準出力を取得
            stderr=True,  # 標準エラーを取得
            remove=True  # 実行後にコンテナを削除
        )

        # 結果をデコードして取得
        output = container.decode("utf-8").strip()
        return output  # 計算結果を返す
    
    except Exception as e:
        return f"Error occurred: {e}"

def docker_calculate(request, pk):
    # クエリパラメータから URL を取得
    url = request.GET.get('url')
    print(url)
    url = "." + url
    diary_object = get_object_or_404(Diary, pk=pk)
    temp_dir = tempfile.mkdtemp()


    #zip_file_local_path = os.path.join(url)
    # ZIPファイルを解凍
    with zipfile.ZipFile(url, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
    

    print(temp_dir)

    # Dockerfile が存在するディレクトリを探す
    temp_dir_docker = None
    for root, dirs, files in os.walk(temp_dir):
        if 'Dockerfile' in files:
            temp_dir_docker = root
            break

    # Dockerfile が見つかった場合、temp_dir_docker にパスが設定される
    if temp_dir_docker:
        print("Dockerfile found in:", temp_dir_docker)
    else:
        print("Dockerfile was not found in the extracted files.")

    if not os.path.exists(os.path.join(temp_dir_docker, "Dockerfile")):
            print("Dockerfileがない")
            return render(request, 'docker_result.html', {'error': 'Dockerfile が見つかりません。'})
    # Dockerコンテナを実行
    #result = run_docker_calculation()
    # Dockerクライアントを作成
    client = docker.from_env()

    
    # Dockerイメージのビルド
    image, build_logs = client.images.build(path=temp_dir_docker, tag="text-to-speech", rm=True)

    host_sample_txt = os.path.join(os.getcwd(), "media") # ホスト側のファイル
    host_sample_txt_path = os.path.join(os.getcwd(), "media", "sample.txt")
    if os.path.exists(host_sample_txt_path):
        logger.info(f"ファイルが存在します: {host_sample_txt_path}")
    else:
        logger.error(f"ファイルが存在しません: {host_sample_txt_path}")
        
    host_output_dir = os.path.join(os.getcwd(), "media","output")  # ホスト側のディレクトリ
    # 計算を実行
    container = client.containers.run(
        image="text-to-speech",  # 実行するイメージ名
        volumes={
            host_sample_txt_path: {'bind': '/app/sample.txt', 'mode': 'ro'},  # sample.txtのマウント
            host_output_dir: {'bind': '/app/output', 'mode': 'rw'}  # outputディレクトリのマウント
        },
        stdout=True,  # 標準出力を取得
        stderr=True,  # 標準エラーを取得
        remove=True  # 実行後にコンテナを削除
    )
    
    # 一時ディレクトリのクリーンアップ
    try:
        os.rmdir(temp_dir)
    except OSError:
        pass

    
    # 結果を新しいテンプレートに渡す
    return render(request, 'docker_result.html', {
        'result': container.decode("utf-8"),  # 計算結果を表示
    })




class FileUploadView(LoginRequiredMixin, OnlyYouMixin, generic.DetailView):
    model = Diary
    template_name = 'diary/diary_detail.html'  # 詳細表示のテンプレート
    
    def post(self, request, *args, **kwargs):
        # Diaryオブジェクトを取得
        diary = self.get_object()
        
        # ファイルが送信されているかチェック
        if request.FILES.get('file'):
            uploaded_file = request.FILES['file']
            
            # サーバーにファイルを保存
            save_path = "./media/temp.txt"  # 保存場所を適切に変更
            with open(save_path, 'wb') as destination:
                destination.write(uploaded_file.read())  # 一括で読み込んで保存
            
            # 保存後にリダイレクトして更新されたページを表示
            return HttpResponseRedirect(reverse('diary:diary_detail', kwargs={'pk': self.kwargs['pk']}))
        
        # それ以外のPOST処理やGETの場合の処理（ファイルアップロードが無い場合）
        return super().post(request, *args, **kwargs)