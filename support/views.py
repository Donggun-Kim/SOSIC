from django.shortcuts import render, redirect, get_object_or_404
from .models import SupportPost, SupportReply
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden

def support_board_list(request):
    category = request.GET.get('category')
    query = request.GET.get('q')
    page_number = request.GET.get('page', 1)

    posts_queryset = SupportPost.objects.all().order_by('-created_at')

    if category:
        posts_queryset = posts_queryset.filter(category=category)

    if query:
        posts_queryset = posts_queryset.filter(
            Q(title__icontains=query) | Q(message__icontains=query)
        )

    paginator = Paginator(posts_queryset, 5)
    page_obj = paginator.get_page(page_number)

    return render(request, 'board_list.html', {
        'posts': page_obj,
        'selected_category': category,
        'is_general': category == "general",
        'is_bug': category == "bug",
        'is_feature': category == "feature",
        'is_account': category == "account",
        'is_other': category == "other"
    })


@login_required
def support_board_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        category = request.POST.get('category')

        # 글 작성
        SupportPost.objects.create(
            user=request.user,
            title=title,
            message=message,
            category=category
        )

        # 여기서 바로 render하지 말고 redirect!
        return redirect('support_board_create_success')

    return render(request, 'board_create.html')


def support_board_create_success(request):
    return render(request, 'board_create_success.html')


def support_board_detail(request, pk):
    post = get_object_or_404(SupportPost, pk=pk)
    reply = getattr(post, 'supportreply', None)
    return render(request, 'board_detail.html', {'post': post, 'reply': reply})


@user_passes_test(lambda u: u.is_staff)
def support_board_reply(request, pk):
    post = get_object_or_404(SupportPost, pk=pk)
    reply = getattr(post, 'supportreply', None)

    if request.method == 'POST':
        reply_text = request.POST.get('reply_text')

        if reply:  # 답변이 있으면 수정
            reply.reply_text = reply_text
            reply.save()
        else:      # 답변이 없으면 새로 작성
            SupportReply.objects.create(
                post=post,
                responder=request.user,
                reply_text=reply_text
            )

        return redirect('support_board_detail', pk=pk)

    # GET: 답변 작성 or 수정 폼 표시
    return render(request, 'board_reply.html', {'post': post, 'reply': reply})


@login_required
def support_board_delete(request, pk):
    post = get_object_or_404(SupportPost, pk=pk)
    if post.user != request.user:
        return HttpResponseForbidden("본인 게시글만 삭제할 수 있습니다.")
    if request.method == 'POST':
        post.delete()
        return redirect('support_board_list')
    return render(request, 'board_delete_confirm.html', {'post': post})


@login_required
def support_board_update(request, pk):
    post = get_object_or_404(SupportPost, pk=pk)

    if request.user != post.user:
        return HttpResponseForbidden("본인 게시글만 수정할 수 있습니다.")

    if request.method == 'POST':
        post.title = request.POST.get('title')
        post.message = request.POST.get('message')
        post.category = request.POST.get('category')
        post.save()
        return redirect('support_board_detail', pk=post.pk)

    return render(request, 'board_update.html', {'post': post})
