from datetime import datetime
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from config import *
import localConfig
import logging
from cbjLibrary.log import initLogger
from sqlUtils import RecorderSql

app = Flask(__name__)
CORS(app, supports_credentials=True)

baseLogger = initLogger(LOG_PATH, BASE_LOGGER_NAME)
logger = logging.getLogger(API_LOGGER_NAME)
sql = RecorderSql(logging.getLogger(STORAGE_LOGGER_NAME))


def verifyToken(func):
    """验证POST的token"""

    def wrapper(*args, **kwargs):
        token = request.json.get(VERIFICATION_COOKIE_NAME)
        logger.info(f"function: {func.__name__}, token: {token}")
        if token is None or token != localConfig.LOGIN_PASSWD:
            return make_response("verification failed")
        return func(*args, **kwargs)

    return wrapper


@app.route("/options", methods=["GET"])
def getOptions():
    """获取所有选项"""
    logger.info(f"get options: {request.args}")
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


@app.route("/tags", methods=["GET"])
def getTags():
    """获取所有标签"""
    logger.info(f"get tags: {request.args}")
    ret = sql.getTags(1)
    return jsonify(ret)


@app.route("/ledger", methods=["POST"])
@verifyToken
def addLedger():
    """记录"""
    logger.info(f"add ledger: {request.json}")
    choice = request.json.get("choice")
    amount = request.json.get("amount")
    tags = request.json.get("tags")
    comment = request.json.get("comment")
    if choice is None or amount is None or tags is None or comment is None:
        return make_response("missing arguments")
    if len(choice) != DEF_CHOICE_LENGTH or choice == DEF_DEFAULT * DEF_CHOICE_LENGTH:
        return make_response("invalid choice")

    sql.insertLedger(choice, amount, tags, comment)
    return make_response("success")


@app.route("/get/ledger", methods=["GET"])
def getLedger():
    """获取记录"""
    logger.info(f"get ledger: {request.args}")
    ledgers = sql.getLedger()
    ret = []
    for ledger in ledgers:
        ret.append([
            datetime.strftime(ledger[0], "%y%m%d:%H"),
            ledger[1],
            str(ledger[2]),
            ledger[3],
            ledger[4],
        ])
    return jsonify(ret)


@app.route("/login", methods=["POST"])
def login():
    """登录"""
    logger.info(f"login: {request.json}")
    passwd = request.json.get("passwd")

    if passwd == localConfig.LOGIN_PASSWD:
        resp = make_response("success")
    else:
        resp = make_response("failed")
    return resp


app.run(localConfig.APP_HOST, localConfig.APP_PORT, ssl_context=(localConfig.SSL_CRT, localConfig.SSL_KEY))
sql.close()
