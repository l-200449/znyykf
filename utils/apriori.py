import pickle

# 获取候选1项集，dataSet为事务集。返回一个list，每个元素都是set集合
def createC1(dataSet):
    C1 = []   # 元素个数为1的项集（非频繁项集，因为还没有同最小支持度比较）
    for transaction in dataSet:
        for item in transaction:
            if not [item] in C1:
                C1.append([item])
    C1.sort()  # 这里排序是为了，生成新的候选集时可以直接认为两个n项候选集前面的部分相同
    # 因为除了候选1项集外其他的候选n项集都是以二维列表的形式存在，所以要将候选1项集的每一个元素都转化为一个单独的集合。
    return list(map(frozenset, C1))   #map(frozenset, C1)的语义是将C1由Python列表转换为不变集合（frozenset，Python中的数据结构）


# 找出候选集中的频繁项集
# dataSet为全部数据集，Ck为大小为k（包含k个元素）的候选项集，minSupport为设定的最小支持度
def scanD(dataSet, Ck, minSupport):
    ssCnt = {}   # 记录每个候选项的个数
    for tid in dataSet:
        for can in Ck:
            if can.issubset(tid):
                ssCnt[can] = ssCnt.get(can, 0) + 1   # 计算每一个项集出现的频率
    numItems = float(len(dataSet))
    retList = []
    supportData = {}
    for key in ssCnt:
        support = ssCnt[key] / numItems
        if support >= minSupport:
            retList.insert(0, key)  #将频繁项集插入返回列表的首部
        supportData[key] = support
    return retList, supportData   #retList为在Ck中找出的频繁项集（支持度大于minSupport的），supportData记录各频繁项集的支持度


# 通过频繁项集列表Lk和项集个数k生成候选项集C(k+1)。
def aprioriGen(Lk, k):
    retList = []
    lenLk = len(Lk)
    for i in range(lenLk):
        for j in range(i + 1, lenLk):
            # 前k-1项相同时，才将两个集合合并，合并后才能生成k+1项
            L1 = list(Lk[i])[:k-2]; L2 = list(Lk[j])[:k-2]   # 取出两个集合的前k-1个元素
            L1.sort(); L2.sort()
            if L1 == L2:
                retList.append(Lk[i] | Lk[j])
    return retList


# 获取事务集中的所有的频繁项集
# Ck表示项数为k的候选项集，最初的C1通过createC1()函数生成。Lk表示项数为k的频繁项集，supK为其支持度，Lk和supK由scanD()函数通过Ck计算而来。
def apriori(dataSet, minSupport=0.5):
    C1 = createC1(dataSet)  # 从事务集中获取候选1项集
    D = list(map(set, dataSet))  # 将事务集的每个元素转化为集合
    L1, supportData = scanD(D, C1, minSupport)  # 获取频繁1项集和对应的支持度
    L = [L1]  # L用来存储所有的频繁项集
    k = 2
    while (len(L[k-2]) > 0): # 一直迭代到项集数目过大而在事务集中不存在这种n项集
        Ck = aprioriGen(L[k-2], k)   # 根据频繁项集生成新的候选项集。Ck表示项数为k的候选项集
        Lk, supK = scanD(D, Ck, minSupport)  # Lk表示项数为k的频繁项集，supK为其支持度
        L.append(Lk)
        supportData.update(supK)  # 添加新频繁项集和他们的支持度
        k += 1
    return L, supportData

def calcu_apriori(datalist, support,savefile = None):
    L,supp=apriori(datalist,minSupport=support)
    #倒序排列
    sortSupp = sorted(supp.items(),key = lambda x:x[1],reverse = True)
    # 将单个元素和多元素分开
    alst = []
    single=[]
    for item in sortSupp:
        if item[1] < support:
            continue
        t=[item]
        if len(item[0]) < 2:
            single = single + t
        else:
            alst = alst+t
    # 保存文件
    if savefile != None:
        with open(savefile, 'wb') as handle:
            pickle.dump(alst, handle, protocol=pickle.HIGHEST_PROTOCOL)
    return single,alst

def load_apriori(file):
    with open(file, 'rb') as handle:
        alst = pickle.load(handle)
    return alst

def getAsso(datasupp, key, minSupp):
    s = set()
    for x in datasupp:
        if x[1] < minSupp:
            continue
        if key in x[0]:
            for k1 in x[0]:
                if k1 == key:
                    continue
                s.add(k1)
    return s

def getAssoCount(datasupp, key, minSupp,minCount):
    s = getAsso(datasupp, key, minSupp)
    while True:
        minSupp = minSupp/2
        if minSupp < 0.001:
            break
        s = getAsso(datasupp, key, minSupp)
        if len(s) > minCount:
            break
    return s