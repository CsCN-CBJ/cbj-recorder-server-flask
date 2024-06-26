class Options:
    def __init__(self, text, value, children: "OptionList" = None):
        self.text = text
        self.value = value
        self.children = children

    def getDict(self) -> dict:
        ret = {"text": self.text, "value": self.value}
        if self.children is not None:
            ret["children"] = self.children.getList()
        return ret


class OptionList:
    def __init__(self, options: list[Options]):
        self.options = options

    def getList(self) -> list[dict]:
        return [op.getDict() for op in self.options] + [{"text": "其他", "value": "O"}]

    def getChild(self, value: str):
        """
        递归获取选项字符串对应的子选项
        """
        for op in self.options:
            if op.value != value[0]:
                continue
            if len(value) > 1:
                return op.children.getChild(value[1:])
            return op.children
        # 允许"其他"选项
        if value == "O":
            return None
        # 非法选项
        raise ValueError(f"Invalid value: {value}")

    def getName(self, value: str):
        """
        递归获取选项值对应的名字
        """
        for op in self.options:
            if op.value != value[0]:
                continue
            if len(value) > 1:
                return op.children.getName(value[1:])
            return op.text
        # 允许"其他"选项
        if value == "O":
            return "其他"
        # 非法选项
        raise ValueError(f"Invalid value: {value}")


doubleFloor = OptionList([
    Options("一楼", "1"),
    Options("二楼", "2"),
])
tripleFloor = OptionList([
    Options("一楼", "1"),
    Options("二楼", "2"),
    Options("三楼", "3"),
])
phoneNumbers = OptionList([
    Options("159", "9"),
    Options("158", "8"),
])

mealChoices = OptionList([
    Options("一食堂", "1", doubleFloor),
    Options("二食堂", "2", tripleFloor),
    Options("三食堂", "3", doubleFloor),
    Options("四食堂", "4", tripleFloor),
    Options("五食堂(麦当劳)", "5"),
    Options("饿了么", "E", phoneNumbers),
    Options("美团", "M", phoneNumbers),
    Options("平山村里", "V"),
])

ledgerOptions = OptionList([
    Options("一日三餐", "M", mealChoices),
    Options("零食饮料", "S"),
    Options("营养保健品", "U", OptionList([
        Options("水果", "F"),
        Options("牛奶", "M"),
        Options("营养品", "S"),
    ])),
    Options("生活日用品", "E"),
    Options("固定支出", "F", OptionList([
        Options("电话", "P"),
        Options("会员", "V"),
    ])),
    Options("娱乐", "N", OptionList([
        Options("外出吃饭", "E"),
    ])),
    Options("交通", "T"),
    Options("医疗", "m"),
])

timeOptions = OptionList([
    Options("工作", "W", OptionList([
        Options("主线", "B"),
        Options("自我", "S"),
        Options("上课", "C"),
        Options("作业", "H"),
    ])),
    Options("睡眠", "Z", OptionList([
        Options("夜晚", "0"),
        Options("午睡", "2"),
        Options("黄昏", "3"),
    ])),
    Options("运动", "X", OptionList([
        Options("跑步", "R"),
        Options("健身", "K"),
        Options("游泳", "S"),
    ])),
    Options("日常", "D", OptionList([
        Options("饮食", "E"),
        Options("洗漱厕", "W"),
        Options("洗衣服", "C"),
        Options("聊天", "T"),
    ])),
    Options("娱乐", "E", OptionList([
        Options("手机", "P", OptionList([
            Options("通用", "C"),
            Options("睡前", "B"),
            Options("睡后", "A"),
        ])),
        Options("电脑", "C"),
        Options("开黑", "F"),
        Options("发呆", "T"),
    ])),
])
