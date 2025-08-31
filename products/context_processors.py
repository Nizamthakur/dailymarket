from .models import HelpVideo

def help_videos(request):
    videos = {}
    try:
        videos['how_to_use_video_url'] = HelpVideo.objects.get(slug='how-to-use-account').video_file.url
    except HelpVideo.DoesNotExist:
        videos['how_to_use_video_url'] = ''
    try:
        videos['placing_order_video_url'] = HelpVideo.objects.get(slug='placing-order').video_file.url
    except HelpVideo.DoesNotExist:
        videos['placing_order_video_url'] = ''
    return videos
