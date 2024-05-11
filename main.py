from flask import Flask, jsonify, request
from flask_cors import CORS
from config import *

app = Flask(__name__)
CORS(app, supports_credentials=True)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route("/users", methods=["GET"])
def get_all_users():
    """获取所有用户信息"""
    print(request.args.get("level"))
    print(request.values.get("parentCode"))
    return jsonify({"code": "200", "msg": "操作成功"})


@app.route("/options", methods=["GET"])
def get_options():
    """获取所有选项"""
    choice = request.args.get("choice")
    ret = []
    if choice is None:
        ret = [
            {OPTIONS_KEY: '一日三餐', OPTIONS_VALUE: LEDGER_TOP_COMMON_MEALS},
            {OPTIONS_KEY: '零食饮料', OPTIONS_VALUE: LEDGER_TOP_SNACKS},
            {OPTIONS_KEY: '营养保健品', OPTIONS_VALUE: LEDGER_TOP_SUPPLEMENTS},
            {OPTIONS_KEY: '生活日用品', OPTIONS_VALUE: LEDGER_TOP_ESSENTIALS},
            {OPTIONS_KEY: '固定支出', OPTIONS_VALUE: LEDGER_TOP_FIXED_COSTS},
            {OPTIONS_KEY: '娱乐', OPTIONS_VALUE: LEDGER_TOP_ENTERTAINMENT},
            {OPTIONS_KEY: '交通', OPTIONS_VALUE: LEDGER_TOP_TRANSPORTATION},
            {OPTIONS_KEY: '医疗', OPTIONS_VALUE: LEDGER_TOP_MEDICAL},
        ]
    elif choice == LEDGER_TOP_COMMON_MEALS:
        ret = [
            {OPTIONS_KEY: '早餐', OPTIONS_VALUE: LEDGER_SEC_BREAKFAST},
            {OPTIONS_KEY: '午餐', OPTIONS_VALUE: LEDGER_SEC_LUNCH},
            {OPTIONS_KEY: '晚餐', OPTIONS_VALUE: LEDGER_SEC_DINNER},
            {OPTIONS_KEY: '夜宵', OPTIONS_VALUE: LEDGER_SEC_SUPPER},
        ]
    elif choice == LEDGER_TOP_FIXED_COSTS:
        ret = [
            {OPTIONS_KEY: '电话', OPTIONS_VALUE: LEDGER_SEC_PHONE},
            {OPTIONS_KEY: '会员', OPTIONS_VALUE: LEDGER_SEC_VIPS},
        ]
    elif choice == LEDGER_TOP_SUPPLEMENTS:
        ret = [
            {OPTIONS_KEY: '水果', OPTIONS_VALUE: LEDGER_SEC_FRUIT},
            {OPTIONS_KEY: '牛奶', OPTIONS_VALUE: LEDGER_SEC_MILK},
        ]
    elif len(choice) == 2 and choice[0] == LEDGER_TOP_COMMON_MEALS:
        ret = [
            {OPTIONS_KEY: '饿了么159', OPTIONS_VALUE: LEDGER_TRD_MEAL_ELM9},
            {OPTIONS_KEY: '饿了么158', OPTIONS_VALUE: LEDGER_TRD_MEAL_ELM8},
            {OPTIONS_KEY: '美团159', OPTIONS_VALUE: LEDGER_TRD_MEAL_MT9},
            {OPTIONS_KEY: '美团158', OPTIONS_VALUE: LEDGER_TRD_MEAL_MT8},
            {OPTIONS_KEY: '一食堂', OPTIONS_VALUE: LEDGER_TRD_MEAL_1},
            {OPTIONS_KEY: '二食堂', OPTIONS_VALUE: LEDGER_TRD_MEAL_2},
            {OPTIONS_KEY: '三食堂', OPTIONS_VALUE: LEDGER_TRD_MEAL_3},
            {OPTIONS_KEY: '四食堂', OPTIONS_VALUE: LEDGER_TRD_MEAL_4},
            {OPTIONS_KEY: '五食堂(麦当劳)', OPTIONS_VALUE: LEDGER_TRD_MEAL_MDL},
        ]

    if len(ret) != 0:
        ret.append({OPTIONS_KEY: '其他', OPTIONS_VALUE: DEF_OTHER})
    return jsonify(ret)


if __name__ == '__main__':
    app.run('localhost', 5000, debug=True)
