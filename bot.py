import random

from urllib.request import urlretrieve

import re, requests, json, os, base64

from pprint import pprint

from cqhttp import CQHttp

from pixivpy3 import *

trace_str = ''

bot = CQHttp(api_root='http://127.0.0.1:5700')
repeat_times = [0, 0, 0]
list_id = [[], [], []]

# 分群组记录复读和上次消息消息和群员昵称
list_group_nickname = [[], [], []]
list_group_id = [391539696, 649092523, 680753147]
list_group_msg = ["", "", ""]

#定义下载图片函数
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
        filename = '{}{}{}{}'.format(file_path, os.sep, file_name, '.jpg')
        # 下载图片，并保存到文件夹中
        urlretrieve(img_url, filename=filename)
    except IOError as e:
        print('文件操作失败', e)
    except Exception as e:
        print('错误 ：', e)



@bot.on_message('group')
def handle_msg(ctx):

    pprint(ctx)
    global repeat_id
    global repeat_group_id
    global group_pos_id

    one_word_url = "https://api.imjad.cn/hitokoto/?cat=&charset=utf-8&length=50&encode=json&fun=sync&source="

    repeat_group_id = ctx['group_id']
    group_pos_id = list_group_id.index(repeat_group_id)
    msg = ctx['message']

    #一言
    if msg == "一言":
        r = requests.get(one_word_url)
        result = json.loads(r.content)
        pprint(result)
        sentance = result['hitokoto'] + '-' +  result['source']
        bot.send_group_msg(group_id=ctx['group_id'], message=sentance)

    #搜番
    if msg.startswith('以图搜番'):
        if re.search(r'url=', msg):
            #pic_url = re.search(r'url=(.*)', msg).group(1)
            file_path = r'C:\Users\Elliot\Desktop\book'
            img_url = re.search(r'url=(.*)', msg).group(1)
            print(img_url)
            save_img(img_url, 'test', file_path)

            #将图片转成base64编码保存到trace_str变量中
            with open(r'C:\Users\Elliot\Desktop\book\test.jpg', 'rb') as f:
                global trace_str
                data = f.read()
                encodestr = base64.b64encode(data)
                trace_str = str(encodestr, 'utf-8')
            #print(trace_str)
            os.remove(r'C:\Users\Elliot\Desktop\book\test.jpg')

            #调用api和整理返回结果
            d = {'image':trace_str}
            s = json.dumps(d)
            r = requests.post('https://trace.moe/api/search', data=s)
            result = json.loads(r.content)
            pprint(result)
            what_min = int(result['docs'][0]['from'] // 60)
            what_sec = int(result['docs'][0]['from'] % 60)
            anime_detail = result['docs'][0]['anime']+'\nepisode {0} time {1}:{2}\n'+'放送时间 {3}\n'+'相似度 百分之{4} '
            anime_detail = anime_detail.format(result['docs'][0]['episode'], what_min, what_sec, result['docs'][0]['season'], int(result['docs'][0]['similarity']*100))
            bot.send_group_msg(group_id=ctx['group_id'], message=anime_detail)

	#天气
    if re.search(r'(.+)天气$', msg):
        city = re.search(r'(.+)天气$', msg).group(1)
        payload = {'address': city, 'tdsourcetag': 's_pcqq_aiomsg'}
        r = requests.get('https://api.imjad.cn/weather/v1/', params=payload)
        result = json.loads(r.content)
        wea_msg = '{}, 最高温:{}, 最低温:{}, pm2.5均值:{}, 感冒易发程度:{}, 整体感觉:{}, {}'.format(result['result']['hourly']['description'], int(result['result']['daily']['temperature'][0]['max']), int(result['result']['daily']['temperature'][0]['min']), int(result['result']['daily']['pm25'][0]['avg']), result['result']['daily']['coldRisk'][0]['desc'], result['result']['daily']['comfort'][0]['desc'], result['result']['forecast_keypoint'])
        bot.send_group_msg(group_id=ctx['group_id'], message=wea_msg)
		


    # 复读检测
    if repeat_times[group_pos_id] == 0:
        list_group_msg[group_pos_id] = msg
        repeat_id = ctx['user_id']
        # 单人复读注释掉下面这几句
        # repeat_times[group_pos_id] += 1
        # list_id[group_pos_id].append(ctx['user_id'])
        # list_group_nickname[group_pos_id].append(ctx['sender']['nickname'])

    if msg == list_group_msg[group_pos_id]:# and repeat_id != ctx['user_id']:
        repeat_times[group_pos_id] += 1
        list_id[group_pos_id].append(ctx['user_id'])
        list_group_nickname[group_pos_id].append(ctx['sender']['nickname'])
        repeat_id = ctx['user_id']

    if msg != list_group_msg[group_pos_id]:
        repeat_times[group_pos_id] = 1
        list_group_msg[group_pos_id] = msg
        repeat_id = ctx['user_id']

        # 重置记录的群员名单,qq号
        list_group_nickname[group_pos_id].clear()
        list_id[group_pos_id].clear()
        list_id[group_pos_id].append(ctx['user_id'])
        list_group_nickname[group_pos_id].append(ctx['sender']['nickname'])

    #print('\n', list_id[group_pos_id], '\n' , list_group_nickname[group_pos_id], '\n%d   %d\n' % (group_pos_id, ctx['user_id']))

    if repeat_times[group_pos_id] == 4:
        bot.send_group_msg(group_id=ctx['group_id'], message='滴滴滴,发现大量复读姬出没,下面我要抓一个小朋友来口球,到底是谁这么幸运呢')
        ban_sec = random.randint(10, 60)
        ban_id = random.randint(0, 3)
        repeat_times[group_pos_id] = 0
        bot.send_group_msg(group_id=ctx['group_id'], message='就决定是你了！复读姬%d号,@%s' % (ban_id+1, list_group_nickname[group_pos_id][ban_id]))
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
    elif re.search(r'二木|木头',msg):
        if ctx['group_id'] == 391539696:
            bot.send_group_msg(group_id=ctx['group_id'], message='说木头是不对的哦,要好好调教一下才行呢,作为惩罚,口球你12小时')
            bot.set_group_ban(group_id=ctx['group_id'], user_id=ctx['user_id'], duration=3600*12)

    elif re.search(r'燕坚', msg):
        bot.send_group_msg(group_id=ctx['group_id'], message='你喊这个呆瓜做什么')

    elif msg.startswith('口我'):
        if re.match(r'^口我(\d{1,8})',msg):
            ban_sec = int(re.match(r'^口我(\d{1,20})',msg).group(1))
            if ban_sec <= 10000:
                bot.send_group_msg(group_id=ctx['group_id'], message='就是你想要被口球吗,真是变态呢,就满足你这次吧')
                bot.set_group_ban(group_id=ctx['group_id'], user_id=ctx['user_id'], duration=ban_sec)
            elif ban_sec >= 10086 and ban_sec < 123456789:
                bot.send_group_msg(group_id=ctx['group_id'], message='蛤？你是抖M吗,居然要求被口%d秒' % ban_sec)
            elif 10000 < ban_sec < 10086:
                bot.send_group_msg(group_id=ctx['group_id'], message='如果你像小狗一样跪下来求我也不是不可以')
            else:
                bot.send_group_msg(group_id=ctx['group_id'], message='嘻嘻嘻那可是你自找的')
                bot.set_group_ban(group_id=ctx['group_id'], user_id=ctx['user_id'], duration=ban_sec)

        else:
            ban_sec = random.randint(30, 120)
            if ctx['group_id'] == 391539696:
                bot.send_group_msg(group_id=ctx['group_id'], message='你是笨蛋吗?没有时间怎么口球,作为惩罚，妲己宝宝口球你%d秒' % ban_sec)
            else:
                bot.send_group_msg(group_id=ctx['group_id'], message='你是笨蛋吗?没有时间怎么口球,作为惩罚，口球你%d秒' % ban_sec)
            bot.set_group_ban(group_id=ctx['group_id'], user_id=ctx['user_id'], duration=ban_sec)

    #主动调用禁言
    if msg.startswith('ban') and (ctx['user_id'] == 1821726849 or ctx['user_id'] == 953075867):
        ban_other_id = re.match(r'^ban\s+(\d{6,10})\s+(\d{1,6})', msg).group(1)
        ban_other_min = re.match(r'^ban\s+(\d{6,10})\s+(\d{1,6})', msg).group(2)
        #两类型都是str
        bot.set_group_ban(group_id=ctx['group_id'], user_id=int(ban_other_id), duration=int(ban_other_min) * 60)
    #主动解禁
    if msg.startswith('free') and ctx['user_id'] == 1821726849:
        free_id = int(re.match(r'^free\s+(\d{6,10})', msg).group(1))
        bot.set_group_ban(group_id=ctx['group_id'], user_id=free_id, duration=0)




# 进群欢迎语
@bot.on_notice('group_increase')
def handle_group_increase(context):
    bot.send(context, message='为大家捕捉到一个网瘾少年,大家快来欢(tiao)迎(jiao)他吧 @%s' % ctx['sender']['nickname'], auto_escape=True)

#私聊调用
@bot.on_message('private')
def handle_msg_self(ctx):
    msg = ctx['message']
    if ctx['user_id'] == 1821726849:
        if msg.startswith('ban'):
            ban_group_id = re.match(r'^ban\s+(\d{6,10})\s+(\d{6,11})\s+(\d{1,6})', msg).group(1)
            ban_other_id = re.match(r'^ban\s+(\d{6,10})\s+(\d{6,11})\s+(\d{1,6})', msg).group(2)
            ban_other_min = re.match(r'^ban\s+(\d{6,10})\s+(\d{6,11})\s+(\d{1,6})', msg).group(3)
            #两类型都是str
            print(ban_group_id, ban_other_id, ban_other_min)
            bot.set_group_ban(group_id=int(ban_group_id), user_id=int(ban_other_id), duration=int(ban_other_min) * 60)

        if msg.startswith('free'):
            free_group_id = int(re.match(r'^free\s+(\d{6,10})\s+(\d{6,10})', msg).group(1))
            free_other_id = int(re.match(r'^free\s+(\d{6,10})\s+(\d{6,10})', msg).group(2))
            bot.set_group_ban(group_id=free_group_id, user_id=free_other_id, duration=0)
bot.run('127.0.0.1', 8080)