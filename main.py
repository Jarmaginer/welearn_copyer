import json
import re
import sys
from random import randint
from time import sleep
import requests


#在这里替换成任意有效的cookie即可 需要完整复制 较长
cookieraw = """双击粘贴在此处"""
#这里写想要复制学习内容的复制对象uid
target_uid = 8694551
#在这里填入要被同步(被刷)的uid列表
stu_uids = [8694551,8694552,8694553,8694554]
#这会将target_uid的学习内容同步到stu_uids列表中的所有uid中

#设置每节课的学习时间的随机数取值(秒) 这将直接显示在学习记录中
time = randint(10, 20)

headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Cookie': cookieraw,
    'Host': 'welearn.sflep.com',
    'Origin': 'https://welearn.sflep.com',
    'Referer': 'https://welearn.sflep.com/student/StudyCourse.aspx',
    'Sec-Ch-Ua': '"Chromium";v="124", "Microsoft Edge";v="124", "Not-A.Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
    'X-Requested-With': 'XMLHttpRequest'
}

#获取想要复制的uid对方的课程学习提交内容
def get_uid_contexts(cid,id,uid):
        dataz = {
            'action': 'getscoinfo_v7',
            'cid': cid,
            'scoid': id,
            'uid': uid,
            'nocache': '0.5561735273317259'
        }
        response = requests.post('https://welearn.sflep.com/Ajax/SCO.aspx?uid='+uid, headers=headers, data=dataz)
        js = json.loads(response.text)
        data = js['comment']
        return data

session = requests.Session()
def printline():
    print('-'*51)




# 读入cookieraw
try:
    cookie = dict(map(lambda x:x.split('=',1),cookieraw.split(";")))
except:
    input('Cookie输入错误!!!')
    exit(0)
for k,v in cookie.items():
        session.cookies[k]=v
printline()



while True:
    # 查询课程信息
    url = "https://welearn.sflep.com/ajax/authCourse.aspx?action=gmc"
    try:
        response = session.get(
            url, headers={"Referer": "https://welearn.sflep.com/student/index.aspx"})

        if '\"clist\":[]}' in response.text:
            input('发生错误!!!可能是登录错误或没有课程!!!')
            exit(0)
        else:
            print('查询课程成功!!!')
            printline()
            print('我的课程: \n')
        back = response.json()["clist"]
        for i, course in enumerate(back, start=1):
            print(f'[NO.{i:>2}] 拷贝度{course["per"]:>3}% {course["name"]}')
    except:
        input('Cookie失效!!!请复制完整')
        exit(0)
    # 选择课程
    order = int(input("\n请输入需要拷贝的课程序号（上方[]内的数字）: "))
    cid = back[order - 1]["cid"]
    printline()
    print("获取单元中...")
    printline()

    # 刷课模块
    url = f"https://welearn.sflep.com/student/course_info.aspx?cid={cid}"
    response = session.get(url)

    uid = re.search('"uid":(.*?),', response.text).group(1)
    classid = re.search('"classid":"(.*?)"', response.text).group(1)

    url = 'https://welearn.sflep.com/ajax/StudyStat.aspx'
    response = session.get(url,params={'action':'courseunits','cid':cid,'uid':uid},headers={'Referer':'https://welearn.sflep.com/student/course_info.aspx'})
    back = response.json()['info']

    # 选择单元 使用了WELearnToSleeep的代码
    print('[NO. 0]  按顺序拷贝全部单元课程')
    unitsnum = len(back)
    for i,x in enumerate(back,start=1):
        if x['visible']=='true':
            print(f'[NO.{i:>2d}]  [已开放]  {x["unitname"]}  {x["name"]}')
        else:
            print(f'[NO.{i:>2d}] ![未开放]! {x["unitname"]}  {x["name"]}')
    unitidx = int(input('\n\n请选择需要拷贝的单元序号（上方[]内的数字，输入0为按顺序刷全部单元）： '))
    printline()

    # 伪造请求
    way1Succeed, way2Succeed, way1Failed, way2Failed = 0, 0, 0, 0

    ajaxUrl = "https://welearn.sflep.com/Ajax/SCO.aspx"
    infoHeaders = {
        "Referer": f"https://welearn.sflep.com/student/course_info.aspx?cid={cid}",
    }

    if(unitidx == 0):
        i = 0
    else:
        i = unitidx - 1
        unitsnum = unitidx

    

    while True:
        response = session.get(
            f'https://welearn.sflep.com/ajax/StudyStat.aspx?action=scoLeaves&cid={cid}&uid={uid}&unitidx={i}&classid={classid}', headers=infoHeaders)

        if "异常" in response.text or "出错了" in response.text:
            break
        if True: 
            for course in response.json()["info"]:
                if course['isvisible']=='false':
                    print(f'[!!跳过!!]    {course["location"]}')
                elif True:  # 章节未拷贝
                    print(f'[即将拷贝]    {course["location"]}')

                    id = course["id"]
                    for uid in stu_uids:
                        print(f'正在将{target_uid}的学习内容复制到{uid} 课程为{course["location"]}')
                        session.post(ajaxUrl, data={"action": "startsco160928",
                                                    "cid": cid,
                                                    "scoid": id,
                                                    "uid": uid
                                                    },
                                    headers={"Referer": f"https://welearn.sflep.com/Student/StudyCourse.aspx?cid={cid}&classid={classid}&sco={id}"})

                    data = get_uid_contexts(cid,id,str(target_uid))

                    print(str(time)+"s时间后post")
                    sleep(time)

                    for uid in stu_uids:
                        response = session.post(ajaxUrl, data={"action": "setscoinfo",
                                                            "cid": cid,
                                                            "scoid": id,
                                                            "uid": uid,
                                                            "data": data,
                                                            "isend": "False" },
                                                headers={"Referer": f"https://welearn.sflep.com/Student/StudyCourse.aspx?cid={cid}&classid={classid}&sco={id}"})
                        if '"ret":0' in response.text:
                            print(str(uid) + "方式1:成功!!!", end="  ")
                            way1Succeed += 1
                        else:
                            print(str(uid) + "方式1:失败!!!", end="  ")
                            way1Failed += 1

                        response = session.post(ajaxUrl, data={"action": "savescoinfo160928",
                                                            "cid": cid,
                                                            "scoid": id,
                                                            "uid": uid,
                                                            "progress": "100",
                                                            "crate": "100",
                                                            "status": "unknown",
                                                            "cstatus": "completed",
                                                            "trycount": "0",
                                                            },
                                                headers={"Referer": f"https://welearn.sflep.com/Student/StudyCourse.aspx?cid={cid}&classid={classid}&sco={id}"})

                        if '"ret":0' in response.text:
                            print(str(uid) + "方式2:成功!!!")
                            way2Succeed += 1
                        else:
                            print(str(uid) + "方式2:失败!!!")
                            way2Failed += 1
                else:  # 章节已拷贝
                    print(f'[ 已拷贝 ]    {course["location"]}')

        if unitidx != 0:
            break
        else:
            i += 1
    if unitidx == 0:
        break
    else:
        print('本单元运行完毕！回到选课处！！\n\n\n\n')
        printline()

printline()
print(f"""
***************************************************
全部拷贝!!

总计:
方式1: {way1Succeed} 成功, {way1Failed} 失败
方式2: {way2Succeed} 成功, {way2Failed} 失败

********************""")
input("按任意键退出")
