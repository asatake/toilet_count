#! /usr/bin/python
# encoding: utf-8

import twitter as tw
import os
import configparser
import re
import sqlite3 as sq3

# config.iniを読み込み
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
oauth_config = config['oauth']

consumer = oauth_config['consumer']
consumer_secret = oauth_config['consumer_secret']
token = oauth_config['token']
token_secret = oauth_config['token_secret']

# OAuth情報を記憶
oauth = tw.OAuth(
    consumer_key=consumer,
    consumer_secret=consumer_secret,
    token=token,
    token_secret=token_secret)

# TwitterApiにauth情報を投げる
t = tw.Twitter(
    auth=tw.OAuth(
        token,
        token_secret,
        consumer,
        consumer_secret)
)

# 自分のscreen_nameを覚える
my_name = '@' + t.account.settings()['screen_name']

# userstreamを取得する準備
tw_us = tw.TwitterStream(auth=oauth, domain='userstream.twitter.com')


# 「トイレ」とつぶやかれていたら回数をカウント
def count_toilet(user, ct):
    conn = sq3.connect(os.path.join(os.path.dirname(__file__), 'toilet.db'))
    cur = conn.cursor()

    # とりあえず初回はテーブル作る
    try:
        cur.execute('''
        create table toilet (
        name text,
        total integer,
        daily integer,
        switch integer
        );
        ''')
        conn.commit()
        count_toilet(user, ct)
    except:
        pass
    # ユーザのデータを取得
    cur.execute('select * from toilet where name="{0}";'.format(user))
    data = cur.fetchone()

    if data is None:  # 該当の名前のレコードがない場合
        # レコード作成
        cur.execute('''insert into toilet
        (name, total, daily, switch)
        values("{0}", 0, 0, 0);
        '''.format(user))
        cur.execute('select * from toilet where name="{0}";'.format(user))
        data = cur.fetchone()

    # 総計に加算
    cur.execute(
        'update toilet set total={0[1]}+{1} where name="{0[0]}";'
        .format(data, ct))
    # デイリーに加算
    cur.execute(
        'update toilet set daily={0[2]}+{1} where name="{0[0]}";'
        .format(data, ct))
    conn.commit()
    conn.close()


# リプライをもらったらカウント数を返してあげる
def tell_count(user):
    conn = sq3.connect(os.path.join(os.path.dirname(__file__), 'toilet.db'))
    cur = conn.cursor()
    try:
        cur.execute('select * from toilet where name="{0}";'
                    .format(user))
        data = cur.fetchone()
        conn.close()
        t.statuses.update(
            status='@' + user + ' あなたは今日{0}回、合計{1}回、トイレと言いました。'
            .format(data[2], data[1]),
            in_reply_to_status_id=msg['id'])
        return
    except:
        conn.close()
        t.statuses.update(
            status='@' + user + ' まだあなたは"トイレ"とつぶやいていません。',
            in_reply_to_status_id=msg['id'])
        return

# userstreamからツイートを読み込んでbotを動かす
for msg in tw_us.user():
    try:
        if 'text' in msg:
            txt = msg['text']
            pat = re.compile('トイレ|ﾄｲﾚ|toire')
            user = msg['user']['screen_name']
            # トイレとつぶやいていたらdbに追加・加算
            if 'text' in msg and (pat.search(txt)):
                f = pat.findall(txt)
                count_toilet(user, len(f))

            # リプライをもらったら今のカウント数を返信する
            if 'text' in msg and txt.startswith(my_name):
                tell_count(user)
    except tw.TwitterHTTPError:
        pass
