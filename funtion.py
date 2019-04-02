import random, time, datetime, urllib
from PIL import Image
from urllib.request import urlretrieve
from bs4 import BeautifulSoup
import re, requests, json, os, base64

from pprint import pprint
from cqhttp import CQHttp

bot = CQHttp(api_root='http://127.0.0.1:5700')

# 分群组记录复读和上次消息消息和群员昵称
list_group_nickname = [[], [], [], []]
list_group_id = [391539696, 649092523, 680753147, 613235799]
list_group_msg = ["", "", "", ""]
# 初始复读次数都为0
repeat_times = [0, 0, 0, 0]
# 记录下各个群的复读id
list_id = [[], [], [], []]

global repeat_group_id
global group_pos_id


trace_str = ''
lesson_list = ['QAQ今天没课哦,请选择C# PHP jacascript中的一门进行学习哦',
               '周一:\n一二节: 大学物理B(1)-(1-16周)-三江楼605\n三四节: 线性代数(1-8周)-三江楼504\n五六节: 高等数学A(II)-(1-15周)-单周-三江楼401', '周二:\n'
                                                                                           'QAQ今天没课哦,但是双周12节要做义工呢',
               '周三:\n一二节: 大学物理实验(物理实验楼)-(4-8周)\n三四节: '
               '中国近代史纲要-(1-13周)-单周-三江楼404\n七八节: 高等数学A(II)-(1-16周)-三江楼401\n晚上: 企业知识产权协同战略(校选-3-15周)-三山楼306',
               '周四:\n一二节: 大学物理B(1)-三江楼605-(2-16周-双周)\n三四节: 高等数学A(II)-(1-16周)-三江401\n五六节: 线性代数(1-8周)-三江楼504\n'
               '七八节: 玉器鉴赏(校选3-14周)-三山楼305',
               '周五:\n一二节: 面向对象程序设计A-(1-16周)-三江楼411\n三四节: 中国近代史纲要-(1-14周)三江404', 'QAQ今天没课哦', 'QAQ今天没课哦']


# 定义下载图片函数
def save_img(img_url, file_name, file_path='book'):
    # 保存图片到磁盘文件夹 file_path中，默认为当前脚本运行目录下的 book文件夹
    try:
        if not os.path.exists(file_path):
            print('文件夹', file_path, '不存在，重新建立')
            # os.mkdir(file_path)
            os.makedirs(file_path)

        # 获得图片后缀,cq不需要
        # file_suffix = os.path.splitext(img_url)[1]

        # 拼接图片名（包含路径）
        filename = '{}{}{}{}'.format(file_path, os.sep, file_name, '.png')
        # 下载图片，并保存到文件夹中
        urlretrieve(img_url, filename=filename)
    except IOError as e:
        print('文件操作失败', e)
    except Exception as e:
        print('错误 ：', e)


"""
代码重构区
"""


def one_message():
    one_word_url = "https://api.imjad.cn/hitokoto/?cat=&charset=utf-8&length=50&encode=json&fun=sync&source="
    r = requests.get(one_word_url)
    result = json.loads(r.content)
    pprint(result)
    sentance = result['hitokoto'] + '-' + result['source']
    return sentance


def search_pic(ctx, msg):
    img_url = re.search(r'url=(.*)', msg).group(1)
    FORMAT_URL = 'https://saucenao.com/search.php?db=6&output_type=2&testmode=1&numres=16&url={}'
    url = FORMAT_URL.format(img_url)

    r = requests.get(url)
    # pprint(r.text)
    res = json.loads(r.content)

    reply = '搜图结果为:\n'
    img_link = res['results'][0]['data'].get('ext_urls', '暂无相关信息')
    title = res['results'][0]['data'].get('title', '暂无相关信息')
    author = res['results'][0]['data'].get('member_name', '暂无相关信息')
    similarity = res['results'][0]['header']['similarity']
    pixiv_id = res['results'][0]['data'].get('pixiv_id', '暂无相关信息')
    print(similarity)
    reply += f'图片直链: {img_link}\ntitle: {title}\npixiv_id: {pixiv_id}\nauthor: {author}'
    if float(similarity) <= 50:
        bot.send_group_msg(group_id=ctx['group_id'], message='在Pixiv没有找到相应的内容哦QAQ,由于只收录了Pixiv接口,咱无能为力呢')
        return
    #  pixiv_id = res['results'][0]['data'].get('pixiv_id', '暂无相关信息')
    r_exist = json.loads(requests.get('https://api.imjad.cn/pixiv/v2/?type=illust&id={}'.format(pixiv_id)).content)
    if r_exist.get('error') != None:
        if r_exist['error']['user_message'] != '':
            bot.send_group_msg(group_id=ctx['group_id'], message='点图姬找到了图片的信息,但是它已经被P站删除了')
            return
        else:
            bot.send_group_msg(group_id=ctx['group_id'], message=reply)
            return
    bot.send_group_msg(group_id=ctx['group_id'], message=reply)


def search_hbook(ctx, msg):
    img_url = re.search(r'url=(.*)', msg).group(1)
    FORMAT_URL = 'https://saucenao.com/search.php?db=999&output_type=2&testmode=1&numres=16&url={}'
    url = FORMAT_URL.format(img_url)
    r = requests.get(url)
    res = json.loads(r.content)

    similarity = res['results'][0]['header'].get('similarity')
    if float(similarity) < 70:
        bot.send_group_msg(group_id=ctx['group_id'], message='404 Not Found!找不到相应结果惹')
        return
    reply = '搜本结果为:\n'
    author = res['results'][0]['data'].get('creator', '无相关信息')
    eng_name = res['results'][0]['data'].get('eng_name', 'QAQ没有相关信息哦')
    jp_name = res['results'][0]['data'].get('jp_name', 'QAQ没有相关信息哦')
    reply += f'相似度: {similarity}\nauthor: {author}\neng_name: {eng_name}\njp_name: {jp_name}'
    bot.send_group_msg(group_id=ctx['group_id'], message=reply)


def search_anime(ctx, msg):
    # add gif search
    if re.search(r"gif", msg):
        img_url = re.search(r'url=(.*)', msg).group(1)
        r = requests.get(img_url)
        with open(r'C:\Users\Administrator\Desktop\book\test.gif', 'wb') as f:
            f.write(r.content)

        im = Image.open(r'C:\Users\Administrator\Desktop\book\test.gif')
        try:
            current = im.tell()
            im.save(r'C:\Users\Administrator\Desktop\book' + '/' + "test" + ".png")
        except EOFError:
            pass
        im.close()
        flag = 1


    elif re.search(r'url=', msg):
        # pic_url = re.search(r'url=(.*)', msg).group(1)
        file_path = r'C:\Users\Administrator\Desktop\book'
        img_url = re.search(r'url=(.*)', msg).group(1)
        # print(img_url)
        save_img(img_url, 'test', file_path)
        flag = 1

    if flag:
        # 将图片转成base64编码保存到trace_str变量中
        with open(r'C:\Users\Administrator\Desktop\book\test.png', 'rb') as f:
            global trace_str
            data = f.read()
            encodestr = base64.b64encode(data)
            trace_str = str(encodestr, 'utf-8')
        # print(trace_str)
        # os.remove(r'C:\Users\Administrator\Desktop\book\test.jpg')

        # 调用api和整理返回结果
        d = {'image': trace_str}
        s = json.dumps(d)
        r = requests.post('https://trace.moe/api/search', data=s)
        result = json.loads(r.content)
        # pprint(result)
        what_min = int(result['docs'][0]['from'] // 60)
        what_sec = int(result['docs'][0]['from'] % 60)
        anime_detail = 'name: ' + result['docs'][0][
            'anime'] + '\nepisode: {0}, time: {1}min:{2}s\n' + '放送时间 {3}\n' + '相似度 百分之{4} '
        anime_detail = anime_detail.format(result['docs'][0]['episode'], what_min, what_sec,
                                           result['docs'][0]['season'], int(result['docs'][0]['similarity'] * 100))

        # delete gif
        if re.search(r"gif", msg):
            os.remove(r'C:\Users\Administrator\Desktop\book\test.gif')
        os.remove(r'C:\Users\Administrator\Desktop\book\test.png')
        flag = 0
        bot.send_group_msg(group_id=ctx['group_id'], message=anime_detail)


def search_weather(msg):
    city = re.search(r'(.+)天气$', msg).group(1)
    payload = {'address': city, 'tdsourcetag': 's_pcqq_aiomsg'}
    r = requests.get('https://api.imjad.cn/weather/v1/', params=payload)
    result = json.loads(r.content)
    wea_msg = '{}, 最高温:{}摄氏度, 最低温:{}摄氏度, pm2.5最大值:{}, 平均风速：{}km/h，感冒易发程度:{}, 整体感觉:{}, {}'.format(
        result['result']['hourly']['description'], int(result['result']['daily']['temperature'][0]['max']),
        int(result['result']['daily']['temperature'][0]['min']), int(result['result']['daily']['pm25'][0]['max']),
        int(result['result']['daily']['wind'][0]['avg']['speed']), result['result']['daily']['coldRisk'][0]['desc'],
        result['result']['daily']['comfort'][0]['desc'], result['result']['forecast_keypoint'])
    return wea_msg



def zhihu_daily(ctx):
    STORY_URL_FORMAT = 'https://daily.zhihu.com/story/{}'
    reply = '最新的知乎日报内容如下:\n'
    r = requests.get('https://news-at.zhihu.com/api/4/news/latest', headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36'})
    data = json.loads(r.content)
    for story in data['stories']:
        url = STORY_URL_FORMAT.format(story['id'])
        title = story['title']
        reply += f'\n{title}\n{url}\n'
    bot.send_group_msg(group_id=ctx['group_id'], message=reply)


def search_book(ctx, msg):
    # 提取书名
    keyword = re.match(r'搜书\s*(.+)', msg).group(1)
    # 构造url
    url = 'https://api.douban.com/v2/book/search?q={}'.format(keyword)

    r = requests.get(url)
    # 整理结果并且提取信息
    res = json.loads(r.content)
    author = ','.join(res['books'][0]['author'])
    score = res['books'][0]['rating']['average']
    pubdate = res['books'][0]['pubdate']
    price = res['books'][0]['price']
    L = [item['title'] for item in res['books'][0]['tags']]
    book_tag = ','.join(L)

    reply = f'author: {author}\n 价格: {price},豆瓣得分: {score}, 出版日期: {pubdate}\n标签: {book_tag}'
    bot.send_group_msg(group_id=ctx['group_id'], message=reply)


def search_film(ctx, msg):
    keyword = re.match(r'搜影\s*(.+)', msg).groups(1)
    # 构造url
    url = 'https://api.douban.com/v2/movie/search?q={}'.format(keyword)
    r = requests.get(url)
    reply = ''
    # 整理结果并且提取信息
    res = json.loads(r.content)
    title = res['subjects'][0]['title']
    original_title = res['subjects'][0]['original_title']
    score = res['subjects'][0]['rating']['average']
    film_genres = ','.join(res['subjects'][0]['genres'])
    year = res['subjects'][0]['year']
    actors = ','.join([item['name'] for item in res['subjects'][0]['casts']])
    reply += f'name: {title}\noriginal_name: {original_title}\n 主演: {actors}\n豆瓣得分:{score}(得分为零为未有评分)\n 电影类型: {film_genres}\n year:{year}'

    bot.send_group_msg(group_id=ctx['group_id'], message=reply)


def search_hot_film(ctx):
    r = requests.get('https://api.douban.com/v2/movie/in_theaters?city=b%E5%8C%97%E4%BA%AC&start=0&count=10')

    res = json.loads(r.content)

    reply = '目前前十热映电影(数据来源豆瓣)\n'
    data = res['subjects']
    # 提取内容
    for item in data:
        title = item['title']
        score = item['rating']['average']
        film_genres = ','.join(item['genres'])
        original_title = item['original_title']
        reply += f'name: {title}\noriginal_name: {original_title}\n 豆瓣得分: {score}, 电影类型: {film_genres}\n\n'
    bot.send_group_msg(group_id=ctx['group_id'], message=reply)


def coming_soon(ctx):
    r = requests.get('https://api.douban.com/v2/movie/coming_soon?start=0&count=10')
    # 获取返回
    res = json.loads(r.content)

    reply = '目前前十即将上映电影(数据来源豆瓣)\n'
    data = res['subjects']
    # 提取内容
    for item in data:
        title = item['title']
        film_genres = ','.join(item['genres'])
        original_title = item['original_title']
        reply += f'name: {title}\noriginal_name: {original_title}\n电影类型: {film_genres}\n\n'
    bot.send_group_msg(group_id=ctx['group_id'], message=reply)


def anime_top(ctx):
    r = requests.get(
        'https://bangumi.bilibili.com/media/web_api/search/result?season_version=-1&area=-1&is_finish=-1&copyright=-1&season_status=-1&season_month=1&pub_date=2019&style_id=-1&order=3&st=1&sort=0&page=1&season_type=1&pagesize=20')
    data = json.loads(r.content)
    pprint(data)
    reply = '当前番据索引如下\n'
    for item in data['result']['data']:
        title = item['title']
        play_time = item['order']['play']
        follow = item['order']['follow']
        index_show = item['index_show']
        score = item['order']['score']
        link = item['link']
        reply += f'\n{title},{play_time},{follow},{index_show},{score},{link}\n\n'
    print(reply)
    bot.send_group_msg(group_id=ctx['group_id'], message=reply)


def anime_pub(ctx):
    r = requests.get('https://bangumi.bilibili.com/web_api/timeline_global')
    data = json.loads(r.text)
    reply = "今日更新番剧如下:\n"

    for item in data['result'][6]['seasons']:
        pub_time = item['pub_time']
        pub_index = item['pub_index']
        title = item['title']
        reply += f'title: {title}, 更新至: {pub_index}, 更新时间: {pub_time}\n\n'
    bot.send_group_msg(group_id=ctx['group_id'], message=reply)


def daily_lesson(ctx, msg):
    fortnight = datetime.datetime.now().isocalendar()[1] - 8
    a = time.localtime()
    if msg == '课程表':
        b = int(time.strftime('%w', a))
    else:
        b = int(re.match(r'课程表\s*(\d)', msg).group(1))
    reply = '第{}周,'.format(fortnight) + lesson_list[b]
    bot.send_group_msg(group_id=ctx['group_id'], message=reply)


def hot_topic():
    target = "https://s.weibo.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}
    r = requests.get(url='https://s.weibo.com/top/summary?cate=realtimehot', headers=headers)
    # r.encoding=('utf-8')
    data = BeautifulSoup(r.text)
    tb = data.find('tbody')
    af = BeautifulSoup(str(tb))
    link_name = BeautifulSoup(str(tb)).find_all('a')
    reply = "微博热搜top及前9如下:\n"
    for i in range(0, 9):
        if re.search(r'/weibo\?q=(.*)&', link_name[i].get('href')):
            print(re.search(r'/weibo\?q=(.*)&', link_name[i].get('href')).group(1))
            reply += urllib.parse.unquote(re.search(r'/weibo\?q=(.*)&', link_name[i].get('href')).group(1)) + '\n\n'
        else:
            reply += "暂时无法获取内容\n"
        reply += target + link_name[i].get('href') + '\n\n'
    # print(reply)
    return reply


def always_on(ctx, msg):
    # 复读检测
    # repeat_group_id = ctx['group_id']
    # group_pos_id = list_group_id.index(repeat_group_id)

    repeat_group_id = ctx['group_id']
    group_pos_id = list_group_id.index(repeat_group_id)  # 获取群组id在创建的列表的位置
    if repeat_times[group_pos_id] == 0:
        list_group_msg[group_pos_id] = msg

    if msg == list_group_msg[group_pos_id]:  # and repeat_id != ctx['user_id']:
        repeat_times[group_pos_id] += 1
        list_id[group_pos_id].append(ctx['user_id'])
        list_group_nickname[group_pos_id].append(ctx['sender']['nickname'])
        # repeat_id = ctx['user_id']

    if msg != list_group_msg[group_pos_id]:
        repeat_times[group_pos_id] = 1
        list_group_msg[group_pos_id] = msg
        # repeat_id = ctx['user_id']

        # 重置记录的群员名单,qq号
        list_group_nickname[group_pos_id].clear()
        list_id[group_pos_id].clear()
        list_id[group_pos_id].append(ctx['user_id'])
        list_group_nickname[group_pos_id].append(ctx['sender']['nickname'])

    # print('\n', list_id[group_pos_id], '\n' , list_group_nickname[group_pos_id], '\n%d   %d\n' % (group_pos_id, ctx['user_id']))

    if repeat_times[group_pos_id] == 4:
        bot.send_group_msg(group_id=ctx['group_id'], message='滴滴滴,发现大量复读姬出没,下面我要抓一个小朋友来口球,到底是谁这么幸运呢')
        ban_sec = random.randint(10, 60)
        ban_id = random.randint(0, 3)
        repeat_times[group_pos_id] = 0
        bot.send_group_msg(group_id=ctx['group_id'],
                           message='就决定是你了！复读姬%d号,@%s' % (ban_id + 1, list_group_nickname[group_pos_id][ban_id]))
        bot.set_group_ban(group_id=ctx['group_id'], user_id=list_id[group_pos_id][ban_id], duration=ban_sec)
        # 重置
        list_id[group_pos_id].clear()
        list_group_nickname[group_pos_id].clear()

    # 人工调用复读
    if msg.startswith('echo '):
        bot.send_group_msg(group_id=ctx['group_id'], message=msg[5:])
    elif re.search(r'tg|舔狗|开房', msg):
        bot.send_group_msg(group_id=ctx['group_id'], message='你这个舔狗不得house哦')

    # 脏话禁言
    elif re.search(r'(操你妈|草泥马|王八|煞笔|傻逼|shabi|mmp|sb|碧池|儿子|渣渣|马勒戈壁|辣鸡|兔崽子|智障|沙雕)', msg):
        ban_sec = random.randint(30, 120)
        bot.send_group_msg(group_id=ctx['group_id'], message='说脏话是不对的哦,要好好调教一下才行呢,作为惩罚,口球你%d秒' % ban_sec)
        bot.set_group_ban(group_id=ctx['group_id'], user_id=ctx['user_id'], duration=ban_sec)

    elif re.search(r'燕坚', msg):
        bot.send_group_msg(group_id=ctx['group_id'], message='你喊这个呆瓜做什么')

    elif msg.startswith('口我'):
        if re.match(r'^口我\s*(\d{1,8})', msg):
            ban_sec = int(re.match(r'^口我\s*(\d{1,20})', msg).group(1))
            if ban_sec <= 10000:
                if ban_sec == 0:
                    bot.send_group_msg(group_id=ctx['group_id'], message='你是笨蛋吗?0怎么口球,作为惩罚，妲己宝宝口球你%d分钟' % 10)
                    bot.set_group_ban(group_id=ctx['group_id'], user_id=ctx['user_id'], duration=600)
                else:
                    bot.send_group_msg(group_id=ctx['group_id'], message='就是你想要被口球吗,真是变态呢,就满足你这次吧')
                    bot.set_group_ban(group_id=ctx['group_id'], user_id=ctx['user_id'], duration=ban_sec)
            elif ban_sec >= 10086 and ban_sec < 123456789:
                bot.send_group_msg(group_id=ctx['group_id'], message='蛤？你是抖M吗,居然要求被口%d秒' % ban_sec)
            elif 10000 < ban_sec < 10086:
                bot.send_group_msg(group_id=ctx['group_id'], message='如果你像小狗一样跪下来求我也不是不可以')
            else:
                bot.send_group_msg(group_id=ctx['group_id'], message='嘻嘻嘻那可是你自找的')
                bot.set_group_ban(group_id=ctx['group_id'], user_id=ctx['user_id'], duration=2591940)

        else:
            ban_sec = random.randint(30, 120)
            if ctx['group_id'] == 391539696:
                bot.send_group_msg(group_id=ctx['group_id'], message='你是笨蛋吗?没有时间怎么口球,作为惩罚，妲己宝宝口球你%d秒' % ban_sec)
            else:
                bot.send_group_msg(group_id=ctx['group_id'], message='你是笨蛋吗?没有时间怎么口球,作为惩罚，口球你%d秒' % ban_sec)
            bot.set_group_ban(group_id=ctx['group_id'], user_id=ctx['user_id'], duration=ban_sec)
    # 主动调用禁言
    if msg.startswith('ban') and (ctx['user_id'] == 1821726849 or ctx['user_id'] == 953075867):
        ban_other_id = re.match(r'^ban.+qq=(\d{6,10})]\s*(\d{1,6})', msg).group(1)
        ban_other_min = re.match(r'^ban.+qq=(\d{6,10})]\s*(\d{1,6})', msg).group(2)
        # 两类型都是str
        bot.set_group_ban(group_id=ctx['group_id'], user_id=int(ban_other_id), duration=int(ban_other_min) * 60)
    # 主动解禁
    if msg.startswith('free') and (ctx['user_id'] == 1821726849 or ctx['user_id'] == 953075867):
        free_id = int(re.match(r'^free.+qq=(\d{6,10})', msg).group(1))
        bot.set_group_ban(group_id=ctx['group_id'], user_id=free_id, duration=0)


# 定义定时函数
def loop():
    # 计算时间
    local_time = time.localtime(time.time())
    local_hour = local_time[3]
    if 8 <= local_hour < 18:
        wait_hour = 18 - local_hour
    elif local_hour >= 18:
        wait_hour = 25 - local_hour
    elif 1 <= local_hour < 7:
        wait_hour = 7 - local_hour
    else:
        wait_hour = 1

    local_min = local_time[4]
    local_second = local_time[5]
    wait_time = wait_hour * 3600 - local_min * 60 - local_second
    print(wait_time)
    time.sleep(wait_time)
    while True:


        time_sub = time.localtime()
        # 获取今天周几
        day_is = int(time.strftime('%w', time_sub))
        # 获取今天第几周
        fortnight = datetime.datetime.now().isocalendar()[1] - 8
        reply = '第{}周,'.format(fortnight) + lesson_list[day_is]

        local_time2 = time.localtime(time.time())
        if local_time2[3] == 7:
            bot.send_private_msg(user_id=1821726849, message=reply)
            bot.send_private_msg(user_id=1821726849, message=one_message())
            bot.send_private_msg(user_id=1821726849, message=search_weather('镇江天气'))
            # 解封全员禁言
            bot.set_group_whole_ban(group_id=391539696, enable=False)
            time.sleep(3600)

        if local_time2[3] == 8:
            bot.send_private_msg(user_id=1821726849, message='早哇QAQ,今天的任务是任选PHP C# Javascript学习半小时, 课时作业也要按时完成哦')
            if day_is in [1,3,4,5]:

                time.sleep(6000)
                bot.send_private_msg(user_id=1821726849, message=reply)
                bot.send_private_msg(user_id=1821726849, message=one_message())
                bot.send_private_msg(user_id=1821726849, message=search_weather('镇江天气'))
                time.sleep(10800)
                bot.send_private_msg(user_id=1821726849, message=reply)
                bot.send_private_msg(user_id=1821726849, message=one_message())
                bot.send_private_msg(user_id=1821726849, message=search_weather('镇江天气'))
                time.sleep(9000)
                bot.send_private_msg(user_id=1821726849, message=reply)
                bot.send_private_msg(user_id=1821726849, message=one_message())
                bot.send_private_msg(user_id=1821726849, message=search_weather('镇江天气'))
                time.sleep(10200)
            else:
                time.sleep(36000)  # 下午六点发送消息
                bot.send_private_msg(user_id=1821726849, message=search_weather('镇江天气'))
        local_time2 = time.localtime(time.time())
        if local_time2[3] == 18:
            bot.send_private_msg(user_id=1821726849, message='晚上好喵,今天的规划都完成了吗?')
            bot.send_private_msg(user_id=1821726849, message=one_message())
            time.sleep(25200)  # 晚上一点全群组禁言
        local_time2 = time.localtime(time.time())
        if local_time2[3] == 1:
            bot.set_group_whole_ban(group_id=391539696, enable=True)
            time.sleep(21600)  # 早上七点发送每日课表,解封群组



