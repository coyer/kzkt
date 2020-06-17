from datetime import datetime
import requests
#from bs4 import BeautifulSoup
import urllib3
#from contextlib import closing
import re
import os

#存储根目录，要改的话，这里要改一下
pathroot = 'G:\\public\\网课\\空中课堂'


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
print('欢迎使用爬虫，抓取空中课堂的视频')

use_grade = 0
vpages = 0
vcount = 0

pattern = 'https://alicache.bdschool.cn/public/bdschool/index/static/ali/weike/'
vpattern = 'https://alivcache.bdschool.cn/vd/'

head = {
        'User-Agent': 
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }

# today = datetime.now()
# format_date = today.strftime('%Y/%m/%d')


def download_video(url, filename):
    global vcount
    vcount += 1
    if os.path.exists(filename):
        print('file existed:', filename)
        return True
    
    print('downloading:', filename)
    try:
        r = requests.get(url, headers=head, verify=False, stream=True, timeout=(5, 25))
        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024000):
                f.write(chunk)
            f.close()
    except requests.exceptions.RequestException as e:
        print(e)
        return False
    except Exception as e:
        print(e)
        return False

    print('download success!', filename)
    return True

def writeList(fileName,listdata):
    fp = open(fileName,'w+')
    fp.write(
        "version: 1"+'\n'
        "count: "+ str(len(listdata)) + '\n'
        "{"+'\n'
    )
    for i in listdata:
        fp.write(i+'\n')

    fp.write("}")
    fp.close()
    return True
    
def spider_page(url, grade):
    if grade < 1 or grade > 12:
        return False
        9
    if use_grade > 0 and use_grade != grade:
        return False

    print('spider grade:', grade)

    folder = f'{pathroot}\\{grade}'
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    global vpages, vcount
    vpages += 1
    response = requests.get(url, headers=head, verify=False)
    if response.status_code == 200:
        response.encoding = 'utf-8'
        vtag = re.findall(r'videourl="([^"]+)"',response.text)

        if vtag:
            nametag = re.findall(r'<span id="album_lesson_name">([^"]+)</span>', response.text)
            mp4name = str(vcount + 1)
            if nametag:
                mp4name = nametag[0]
            
            mp4name = mp4name.replace('?', '')
            mp4name = mp4name.replace('\'', '')
            mp4name = mp4name.replace('\\', '')
            
            mp4name = mp4name.strip()

            video_url = vtag[0]
            # print('video url:', video_url)
            # print('video name:', mp4name)

            filename = f'{folder}\\{mp4name}.mp4'
            
            return download_video(video_url, filename)
        else:
            print('no video tag found.')
            return False
    else:
        print('Error to get page:', response.url)
        return False

def spider():
    if not os.path.exists(pathroot):
        print(f'{pathroot},存储目录不存在，请检查目录是否正确')
        return

    #如果需要下载所有视频，把这段代码注释掉即可
    global use_grade
    while use_grade < 1 or use_grade > 12:
        s = input('请输入年级数字，数字(1~12):')
        if s == '':
            use_grade = 0
        else :
            use_grade = int(s)

    response = requests.get('https://alicache.bdschool.cn/public/bdschool/index/static/ali/w.html', headers=head, verify=False)
    if response.status_code == 200:
        response.encoding = 'utf-8'
        hreftag = re.findall(r'href="https://alicache.bdschool.cn/public/bdschool/index/static/ali/weike/([^"]+)"',response.text)
        if hreftag:
            writeList(f'{pathroot}\\list.txt', hreftag)
            for i in hreftag:
                #spider_page(f'{pattern}{i}')
                grade = 0
                rgrade = re.findall('grade_id=([^"]+)&', i)
                if rgrade:
                    grade = int(rgrade[0])
                spider_page(f'{pattern}{i}', grade)

        # soup = BeautifulSoup(response.text, 'html.parser')
        # links - soup.find_all*
        # for link in soup.find_all('a'):
        #     hreftext = link.get('href')
        #     if hreftext.startswith(pattern):
        #         spider_page(hreftext)
    else :
        print('Error:', response.url)


spider()

print('page count:', vpages)
print('video count:', vcount)

print('spidder end.')