from pytube import YouTube


def download_from_youtube(link: str):
    yt = YouTube(link)
    print('start downloading video')
    video = yt.streams.first().download()
    print('video downloaded - ', video)
    return video
