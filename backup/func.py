from random import choices, sample, shuffle

Nums = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
upChs = ['A', 'B', 'C', 'D', 'E', 'F', 'G',
         'H', 'I', 'J', 'K', 'L', 'M', 'N',
         'O', 'P', 'Q', 'R', 'S', 'T',
         'U', 'V', 'W', 'X', 'Y', 'Z']
lowChs = ['a', 'b', 'c', 'd', 'e', 'f', 'g',
          'h', 'i', 'j', 'k', 'l', 'm', 'n',
          'o', 'p', 'q', 'r', 's', 't',
          'u', 'v', 'w', 'x', 'y', 'z']
# 去除 ' & "字符
spPwdChs = ['!', ',', '.', '?', ';', ':',
            '~', '@', '#', '$', '%', '&', '_']
spAdChs = ['~', '!', '@', '#', '$', '%', '&', '*', '?']
uchs = 'DZVUEROALWMIXCPJSYBKTHNGFQ'
lchs = 'diyslvcnhwojqkzuptbeamfxgr'
chs = uchs + lchs
nums = '7156420938'
achs = '%@$?#*~!&'
pchs = '.$@;_#:%&~?!,'


# repet -> 允许重复
def randomstr(s, slen, repet=True):
    if slen < 1:
        return ''
    if repet:
        return ''.join(choices(s, k=slen))
    return ''.join(sample(s, slen))


def getAdIDs(counts, levels):
    n = len(counts)
    AdIDs = []
    for i in range(n):
        IDs = []
        for j in range(counts[i]):
            p1, p2, p3 = randomstr(nums, 4), randomstr(lchs, 5), randomstr(uchs, 5)
            p4 = randomstr(chs, 4) + randomstr(achs, levels[i])
            # 除去特殊字符
            p5 = randomstr(nums + chs, 10 - levels[i])
            ID = '%s-%s-%s-%s-%s' % (p1, p2, p3, p4, p5)
            IDs.append(ID)
        AdIDs.append(IDs)
    return AdIDs


def checkPwd(pwd):
    n = len(pwd)
    if n < 9 or n > 16:
        print('pwd len is not correct!')
        return 1
    empty, pwd_set = set(), set(pwd)
    nums_set, chs_set, pchs_set = set(nums), set(chs), set(pchs)
    if pwd_set & nums_set == empty:
        print('pwd must contain number!')
        return 2
    if pwd_set & chs_set == empty:
        print('pwd must contain chs!')
        return 3
    if pwd_set & pchs_set == empty:
        print('pwd must contain spchs!')
        return 4
    if pwd_set - nums_set - chs_set - pchs_set != empty:
        print('pwd contain unknown chs!')
        return 5
    return 0


def checkAdID(AdID):
    if len(AdID) != 32:
        print('AdID len is not correct!')
        return 1
    s = AdID.split('-')
    if len(s) != 5:
        print('AdID format is not correct!')
        return 1
    empty = set()
    nums_set, chs_set, achs_set = set(nums), set(chs), set(achs)
    if len(s[0]) != 4 or set(s[0]) - nums_set != empty:
        print('AdID p1 error!')
        return 2
    if len(s[1]) != 5 or set(s[1]) - set(lchs) != empty:
        print('AdID p2 error!')
        return 3
    if len(s[2]) != 5 or set(s[2]) - set(uchs) != empty:
        print('AdID p3 error!')
        return 4
    if set(s[3][:4]) - chs_set != empty or set(s[3][4:]) - achs_set != empty:
        print('AdID p4 error!')
        return 5
    if set(s[4]) - nums_set - chs_set != empty:
        print('AdID p5 error!')
        return 6
    # 遍历生成且正在使用的AdIDs验证AdID
    return 0


# 随机字符 -> random.choice(uchs+lchs)
# 随机字符串(list) -> random.choice(str, k=N)
# 随机字符串(list) -> random.sample(str, N)
# ''.join(list)
# 洗牌 -> random.shuffle(list)
print('-----------')
# random.shuffle(Nums)
# print(''.join(Nums))
# random.shuffle(lowChs)
# print(''.join(lowChs))
# random.shuffle(upChs)
# print(''.join(upChs))
# random.shuffle(spAdChs)
# print(''.join(spAdChs))
# random.shuffle(spPwdChs)
# print(''.join(spPwdChs))
print('-----------')
# cts, lvls = [20, 30, 40, 50], [1, 2, 3, 4]
# AdIDs = getAdIDs(cts, lvls)
# for AdID in AdIDs:
#     print(AdID)
print('-----------')
# pwds = ['ewa933',  '893jhosue9nsde9ru34jreo', '123456789', 'uhwjosold', '12idsk378', '1234.<*YGE', '0251x.fy..22216']
# for pwd in pwds:
#     if checkPwd(pwd) == 0:
#         print(pwd)
print('-----------')
AdIDs = ['790-alcdrr-BUORA-GDyr#**&-4JPKbP', '5750-nxaq-QQPFQC-WBfb#@?$-JNFWoP',
         '8607-pbanv-pTMVI-qTFq?$%~-4LbiKh', '7685-wshbp-BOKNX-AoF?%?$?-D7hlUL',
         '4323-dnorw-AHXPT-Fpqf&~&!-IFFLzj', '7440-qrfpf-XOZUZ-anIC!?~&-VsphAv',
         '8000-utsji-GARLW-vhuA@~?%-Ls3T3J', '2365-bgyvw-WTPNX-HIQc*&**-8ZOCJ6']
for AdID in AdIDs:
    if checkAdID(AdID) == 0:
        print(AdID)
