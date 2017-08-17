#!/usr/bin/python
# coding: utf-8
"""
File: $scripts.py
Author: noogel <noogel@163.com>
Date: 2017-08-17
Description: xyzUtils
"""


import sys
import time
import string
import hashlib
import base64
import random
import warnings
from decimal import Decimal

from workflow import Workflow, ICON_INFO, ICON_ERROR, web
from commands import getoutput
import socket
from urlparse import urlparse

CATEGORY_MAP = {
    "ntime": {
        "func": "unixtime_or_datetime_convert",
        "title": u"时间格式转换",
    },
    "nb64d": {
        "func": "base64_decode",
        "title": u"Base64解码",
    },
    "nb64e": {
        "func": "base64_encode",
        "title": u"Base64编码",
    },
    "nhelp": {
        "func": "you_need_help",
        "title": u"帮助文档",
    },
    "nmd5": {
        "func": "generage_md5",
        "title": u"MD5生成",
    },
    "nrdm": {
        "func": "random_string",
        "title": u"随机数生成"
    },
    "nu2c": {
        "func": "unicode_to_char",
        "title": u"Unicode转中文"
    },
    "nc2u": {
        "func": "char_to_unicode",
        "title": u"中文转Unicode"
    },
    "ncny": {
        "func": "cny_capital",
        "title": u"人民币大写"
    },
    "nip": {
        "func": "get_ip_info",
        "title": u"查询 IP 信息"
    }
}


def you_need_help(strs):
    return [{"cmd": key, "title": val["title"]} for key, val in CATEGORY_MAP.items()] + [
        {"cmd": "noogel", "title": u"作者博客"}]


def generage_md5(strs):
    """md5"""
    return hashlib.md5(strs).hexdigest()


def base64_encode(strs):
    return base64.b64encode(strs)


def base64_decode(strs):
    return base64.b64decode(strs)


def unixtime_or_datetime_convert(strs):
    """时间戳与正常时间转换"""
    fmt = "%Y-%m-%d %H:%M:%S"
    try:
        return time.strftime(fmt, time.localtime(int(strs)))
    except:
        return str(int(time.mktime(time.strptime(strs, fmt))))


def random_string(length, is_pun=False):
    rdm_str = string.digits + string.letters
    if is_pun:
        rdm_str += string.punctuation
    return "".join(random.sample(rdm_str, int(length)))


def unicode_to_char(strs):
    return strs.decode("unicode_escape")


def char_to_unicode(strs):
    return strs.encode("unicode_escape")


def cny_capital(value, capital=True, prefix=False, classical=None):
    """
    参数:
    capital:    True   大写汉字金额
                False  一般汉字金额
    classical:  True   元
                False  圆
    prefix:     True   以"人民币"开头
                False, 无开头
    """
    if not isinstance(value, (Decimal, str, int)):
        msg = """
        由于浮点数精度问题，请考虑使用字符串，或者 decimal.Decimal 类。
        因使用浮点数造成误差而带来的可能风险和损失作者概不负责。
        """
        warnings.warn(msg, UserWarning)
    # 默认大写金额用圆，一般汉字金额用元
    if classical is None:
        classical = True if capital else False

    # 汉字金额前缀
    if prefix is True:
        prefix = "人民币"
    else:
        prefix = ""

    # 汉字金额字符定义
    dunit = ("角", "分")
    if capital:
        num = ("零", "壹", "贰", "叁", "肆", "伍", "陆", "柒", "捌", "玖")
        iunit = [None, "拾", "佰", "仟", "万", "拾", "佰", "仟", "亿", "拾", "佰", "仟", "万", "拾", "佰", "仟"]
    else:
        num = ("〇", "一", "二", "三", "四", "五", "六", "七", "八", "九")
        iunit = [None, "十", "百", "千", "万", "十", "百", "千", "亿", "十", "百", "千", "万", "十", "百", "千"]
    if classical:
        iunit[0] = "元" if classical else "圆"
    # 转换为Decimal，并截断多余小数

    if not isinstance(value, Decimal):
        value = Decimal(value).quantize(Decimal("0.01"))

    # 处理负数
    if value < 0:
        prefix += "负"  # 输出前缀，加负
        value = - value  # 取正数部分，无须过多考虑正负数舍入
        # assert - value + value == 0
    # 转化为字符串
    s = str(value)
    if len(s) > 19:
        raise ValueError("金额太大了，不知道该怎么表达。")
    istr, dstr = s.split(".")  # 小数部分和整数部分分别处理
    istr = istr[::-1]  # 翻转整数部分字符串
    so = []  # 用于记录转换结果

    # 零
    if value == 0:
        return prefix + num[0] + iunit[0]
    haszero = False  # 用于标记零的使用
    if dstr == "00":
        haszero = True  # 如果无小数部分，则标记加过零，避免出现“圆零整”

    # 处理小数部分
    # 分
    if dstr[1] != "0":
        so.append(dunit[1])
        so.append(num[int(dstr[1])])
    else:
        so.append("整")  # 无分，则加“整”
    # 角
    if dstr[0] != "0":
        so.append(dunit[0])
        so.append(num[int(dstr[0])])
    elif dstr[1] != "0":
        so.append(num[0])  # 无角有分，添加“零”
        haszero = True  # 标记加过零了

    # 无整数部分
    if istr == "0":
        if haszero:  # 既然无整数部分，那么去掉角位置上的零
            so.pop()
        so.append(prefix)  # 加前缀
        so.reverse()  # 翻转
        return "".join(so)

    # 处理整数部分
    for i, n in enumerate(istr):
        n = int(n)
        if i % 4 == 0:  # 在圆、万、亿等位上，即使是零，也必须有单位
            if i == 8 and so[-1] == iunit[4]:  # 亿和万之间全部为零的情况
                so.pop()  # 去掉万
            so.append(iunit[i])
            if n == 0:  # 处理这些位上为零的情况
                if not haszero:  # 如果以前没有加过零
                    so.insert(-1, num[0])  # 则在单位后面加零
                    haszero = True  # 标记加过零了
            else:  # 处理不为零的情况
                so.append(num[n])
                haszero = False  # 重新开始标记加零的情况
        else:  # 在其他位置上
            if n != 0:  # 不为零的情况
                so.append(iunit[i])
                so.append(num[n])
                haszero = False  # 重新开始标记加零的情况
            else:  # 处理为零的情况
                if not haszero:  # 如果以前没有加过零
                    so.append(num[0])
                    haszero = True

    # 最终结果
    so.append(prefix)
    so.reverse()
    return "".join(so).decode("utf-8")


def get_ip_info(ip):
    """
    通过IP获取地理位置信息
    """

    LOCATION_QUERY_URL = 'http://www.ip138.com/ips138.asp'
    FEATURE_BEGIN_STR = '<td align="center"><ul class="ul1"><li>'
    FEATURE_END_STR = '</li></ul></td>'
    FEATURE_SPLIT_STR = '</li><li>'

    rt = web.get(LOCATION_QUERY_URL, dict(ip=ip, action=2))
    rt.raise_for_status()
    rts = rt.text[
          rt.text.find(FEATURE_BEGIN_STR) + len(FEATURE_BEGIN_STR):
          rt.text.find(FEATURE_END_STR)]
    rtlist = rts.split(FEATURE_SPLIT_STR)

    # 去掉前缀和多余空格，最长的即是最优解
    result = ''
    for val in rtlist:
        rl = val[val.find(u'：') + 1:].strip().split()
        # 对诸如：北京市北京市 这种字符串修整为：北京市
        for i, k in enumerate(rl):
            size = len(k)
            if size % 2 == 0:
                size /= 2
                lhalf = k[:size]
                rhalf = k[size:]
                if lhalf == rhalf:
                    rl[i] = lhalf

        temp = ' '.join(rl)
        if len(temp) > len(result):
            result = temp
    if len(result) > 256:
        result = u"数据解析异常"
    return result


def main(wf):
    # 去掉参数两边的空格
    params = (wf.args or [""])[0].strip().split(" ")
    optype, param = params[0].strip(), " ".join(params[1:]).strip()
    if not param:
        wf.add_item(title=u"请输入内容", subtitle="Cant\'t Empty!", icon=ICON_ERROR)
    elif optype in CATEGORY_MAP:
        conf = CATEGORY_MAP[optype]
        try:
            result = globals()[conf["func"]](param)
        except Exception as ex:
            result = ex.message
        if isinstance(result, basestring):
            wf.add_item(
                title=u"{} 『{}』".format(conf["title"], param),
                subtitle=result,
                arg=result,
                valid=True,
                icon=ICON_INFO)
        elif isinstance(result, list):
            for item in result:
                wf.add_item(
                    title=item["title"],
                    subtitle=item["cmd"],
                    arg=param,
                    valid=True,
                    icon=ICON_INFO)
        else:
            wf.add_item(title=u"暂未收录改返回类型", subtitle="...", icon=ICON_ERROR)
    else:
        wf.add_item(title=u"类型异常", subtitle="...", icon=ICON_ERROR)

    wf.send_feedback()


if __name__ == u"__main__":
    wf = Workflow()
    sys.exit(wf.run(main))
