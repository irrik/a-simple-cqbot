from funtion import *
import threading

# 定义新的线程处理定时任务
t = threading.Thread(target=loop, name='LoopThread')
t.start()

# 监控群消息
@bot.on_message('group')
def handle_msg(ctx):
    pprint(ctx)
    msg = ctx['message']

    #匹配消息关键字 是命令语句就执行操作
    
    # 一言
    if msg == "一言":
        bot.send_group_msg(group_id=ctx['group_id'], message=one_message())

    # 搜图
    if msg.startswith('搜图'):
        search_pic(ctx, msg)

    # 以图搜本
    if msg.startswith('以图搜本'):
        search_hbook(ctx, msg)


    # 搜番
    if msg.startswith('以图搜番'):
        search_anime(ctx, msg)

    if re.search(r'(.+)天气$', msg):
        bot.send_group_msg(group_id=ctx['group_id'], message=search_weather(msg))

    # 知乎日报
    if msg == '知乎日报':
        zhihu_daily(ctx)

    # 豆瓣搜书
    if msg.startswith('搜书'):
        search_book(ctx, msg)

    # 豆瓣搜索电影
    if msg.startswith('搜影'):
        search_film(ctx, msg)

    # 豆瓣热映电影
    if msg == '热映电影':
        search_hot_film(ctx)


    # 即将上映
    if msg == '即将上映':
        coming_soon(ctx)

    # 番据索引
    if msg == '番剧索引':
        anime_top(ctx)


    # 番剧更新
    if msg == '番剧更新':
        anime_pub(ctx)

    # 课程表
    if msg.startswith('课程表') and ctx['user_id'] == 1821726849:
        daily_lesson(ctx, msg)


    # 微博热搜
    if msg == "微博热搜":
        bot.send_group_msg(group_id=ctx['group_id'], message=hot_topic())


    # 消息最后都会经过这一部分 里面封装了幅度检测以及脏话的监禁等
    always_on(ctx, msg)



# 私聊调用
@bot.on_message('private')
def handle_msg_self(ctx):
    msg = ctx['message']
    if ctx['user_id'] == 1821726849:
        if msg.startswith('ban'):
            ban_group_id = re.match(r'^ban\s+(\d{6,10})\s+(\d{6,11})\s+(\d{1,6})', msg).group(1)
            ban_other_id = re.match(r'^ban\s+(\d{6,10})\s+(\d{6,11})\s+(\d{1,6})', msg).group(2)
            ban_other_min = re.match(r'^ban\s+(\d{6,10})\s+(\d{6,11})\s+(\d{1,6})', msg).group(3)
            # 两类型都是str
            print(ban_group_id, ban_other_id, ban_other_min)
            bot.set_group_ban(group_id=int(ban_group_id), user_id=int(ban_other_id), duration=int(ban_other_min) * 60)

        if msg.startswith('free'):
            free_group_id = int(re.match(r'^free\s+(\d{6,10})\s+(\d{6,10})', msg).group(1))
            free_other_id = int(re.match(r'^free\s+(\d{6,10})\s+(\d{6,10})', msg).group(2))
            bot.set_group_ban(group_id=free_group_id, user_id=free_other_id, duration=0)

    if msg.startswith('记录'):
        recordMsg(ctx)

    if msg.startswith("知识点"):
        repeatMsg(ctx)

    if msg.startswith('清空'):
        reSet(ctx)

# 机器人监控了这个端口
bot.run('127.0.0.1', 8080)