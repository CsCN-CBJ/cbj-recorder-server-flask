doubleFloor = {'1': '一楼', '2': '二楼', }
tripleFloor = {'1': '一楼', '2': '二楼', '3': '三楼', }
phoneNumbers = {'9': '159', '8': '158', }

mealChoices = {
    '1': ('一食堂', doubleFloor),
    '2': ('二食堂', tripleFloor),
    '3': ('三食堂', doubleFloor),
    '4': ('四食堂', tripleFloor),
    '5': '五食堂(麦当劳)',
    'E': ('饿了么', phoneNumbers),
    'M': ('美团', phoneNumbers),
    'V': '平山村里',
}

ledgerOptions = {
    'M': ('一日三餐', {
        '1': ('早餐', mealChoices),
        '2': ('午餐', mealChoices),
        '3': ('晚餐', mealChoices),
        '4': ('夜宵', {
            'D': '门口小摊',
        }),
    }),
    'S': '零食饮料',
    'U': ('营养保健品', {
        'F': '水果',
        'M': '牛奶',
        'S': '营养品',
    }),
    'E': '生活日用品',
    'F': ('固定支出', {
        'P': '电话',
        'V': '会员',
    }),
    'N': ('娱乐', {
        'E': '外出吃饭',
    }),
    'T': '交通',
    'm': '医疗',
}
