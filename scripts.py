#!/usr/bin/python
# coding: utf-8
"""
File: $scripts.py
Author: noogel <noogel@163.com>
Date: 2017-08-17
Description: xyzUtils
"""
import re
import sys
import time
import string
import base64
import random
import logging
import hashlib
import datetime

from workflow import Workflow, ICON_INFO, ICON_ERROR, web


logger = logging.getLogger('workflow')


class Utils(object):

    @staticmethod
    def copy_you_input(strs):
        """
        ncp,无格式化粘贴
        :param strs:
        :return:
        """
        return strs

    @staticmethod
    def utf8_to_char(strs):
        """
        nu8c,UTF-8编码转汉字
        :param strs:
        :return:
        """
        return eval(u"\"{}\".decode('utf-8')".format(strs))

    @classmethod
    def you_need_help(cls, strs):
        """
        nhp,帮助文档
        :param strs:
        :return:
        """
        strs = strs.strip()
        result = [{"cmd": "noogel", "title": u"作者博客"}]
        for func in dir(cls):
            if str(func).startswith("_"):
                continue
            cmd, title = parse_func_doc(getattr(cls, func).__doc__)
            if not (cmd or title):
                continue
            # 简单搜索功能
            if strs and strs not in cmd and strs not in title:
                continue
            result.append({"cmd": to_utf8(cmd), "title": to_unicode(title)})
        return result

    @staticmethod
    def generage_md5(strs):
        """
        nmd5,计算MD5值，注意空格
        :param strs:
        :return:
        """
        return hashlib.md5(strs).hexdigest()

    @staticmethod
    def base64_encode(strs):
        """
        nb64e,base64编码
        :param strs:
        :return:
        """
        return base64.b64encode(strs)

    @staticmethod
    def base64_decode(strs):
        """
        nb64d,base64解码
        :param strs:
        :return:
        """
        return base64.b64decode(strs)

    @staticmethod
    def unixtime_or_datetime_convert(strs):
        """
        ntm,时间戳与正常时间转换
        :param strs:
        :return:
        """
        dt_fmt = "%Y-%m-%d"
        fmt = "%Y-%m-%d %H:%M:%S"
        strs = strs.strip()
        if strs == "n":
            return str(int(time.time()))
        elif strs == "t":
            return datetime.datetime.now().strftime(fmt)
        if strs.isdigit():
            return time.strftime(fmt, time.localtime(int(strs)))
        else:
            try:
                return str(int(time.mktime(time.strptime(strs, dt_fmt))))
            except:
                try:
                    return str(int(time.mktime(time.strptime(strs, fmt))))
                except:
                    return "请输入正确格式的时间戳、日期「%Y-%m-%d」、时间「%Y-%m-%d %H:%M:%S」"

    @staticmethod
    def random_string(length, is_pun=False):
        """
        nrdm,生成随机字符串
        :param length:
        :param is_pun:
        :return:
        """
        rdm_str = string.digits + string.letters
        if is_pun:
            rdm_str += string.punctuation
        return ''.join(random.choice(rdm_str) for _ in range(int(length)))

    @staticmethod
    def sum_numbers(strs):
        """
        nsum,简单的数字求和
        :param strs:
        :return:
        """
        numbers = filter(lambda dig: dig.isdigit(), re.split(u"[\n\r\t ,，]", strs))
        result = str(sum([int(val) for val in numbers]))
        return [{"title": u"求和『{}』".format(" + ".join(numbers)), "cmd": result}]

    @staticmethod
    def unicode_to_char(strs):
        """
        nu2c,Unicode转汉字
        :param strs:
        :return:
        """
        strs = strs.replace('\\\\u', '\\u')
        return strs.decode("unicode_escape")

    @staticmethod
    def char_to_unicode(strs):
        """
        nc2u,汉字转Unicode
        :param strs:
        :return:
        """
        return strs.encode("unicode_escape")

    @staticmethod
    def base_reformat(strs):
        """
        nfm,简单的字符串格式化
        :param strs:
        :return:
        """
        return ",".join(map(lambda x: "'{}'".format(x.strip()), filter(lambda x: x.strip(), re.split(r'[\n\t\r]', strs))))

    @staticmethod
    def cny_capital(value, capital=True, prefix=False, classical=None):
        """
        ncny,人民币大写转换
        :param value: 金额
        :param capital: True   大写汉字金额, False  一般汉字金额
        :param prefix: True   以"人民币"开头, False, 无开头
        :param classical: True   元,False  圆
        :return:
        """
        import warnings
        from decimal import Decimal
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

    @staticmethod
    def open_author_blog(strs):
        """noogel,浏览作者博客"""
        import webbrowser
        webbrowser.open("http://noogel.xyz")

    @staticmethod
    def get_ip_info(ip):
        """
        nip,通过IP获取地理位置信息
        :param ip:
        :return:
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


def to_unicode(strs):
    if isinstance(strs, str):
        strs = strs.decode('utf-8')
    return strs


def to_utf8(strs):
    if isinstance(strs, unicode):
        strs = strs.encode("utf-8")
    return strs


def parse_func_doc(doc):
    """解析函数文档"""
    try:
        cmd, title = doc.split(':')[0].replace('\n', '').strip().decode("utf-8").split(",")
        return cmd.strip(), title.strip()
    except Exception:
        return u"", u""


def main(wf):
    # 去掉参数两边的空格
    optype, param = (wf.args or [""])[0].lstrip().split(' ', 1)
    if not param:
        wf.add_item(title=u"请输入内容", subtitle="Cant\'t Empty!", icon=ICON_ERROR)
    elif hasattr(Utils, optype):
        command, title = parse_func_doc(getattr(Utils, optype).__doc__)
        try:
            result = getattr(Utils, optype)(param)
        except Exception as ex:
            result = ex.message
        if isinstance(result, basestring):
            print result
            wf.add_item(
                title=u"{} 『{}』".format(title, param),
                subtitle=result,
                arg=result,
                valid=True,
                icon=ICON_INFO)
        elif isinstance(result, list):
            for item in result:
                wf.add_item(
                    title=item["title"],
                    subtitle=item["cmd"],
                    arg=item["cmd"],
                    valid=True,
                    icon=ICON_INFO)
        else:
            wf.add_item(title=u"暂未收录改返回类型", subtitle="...", icon=ICON_ERROR)
    else:
        wf.add_item(title=u"类型异常", subtitle="检查是否添加了类型字典", icon=ICON_ERROR)

    wf.send_feedback()


if __name__ == u"__main__":
    wf = Workflow()
    sys.exit(wf.run(main))
