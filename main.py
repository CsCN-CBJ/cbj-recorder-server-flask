from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from config import *
import localConfig
import logging
from cbjLibrary.log import initLogger
from sqlUtils import RecorderSql
from options import *
from utils import *

app = Flask(__name__)
CORS(app, supports_credentials=True)

baseLogger = initLogger(LOG_PATH, BASE_LOGGER_NAME)
logger = logging.getLogger(API_LOGGER_NAME)
sql = RecorderSql(logging.getLogger(STORAGE_LOGGER_NAME))


def makeSuccessResponse():
    return make_response("success")


def makeFailedResponse(response: str):
    return make_response(response, 206)


def verifyToken(func):
    """验证POST的token"""

    def wrapper(*args, **kwargs):
        token = request.json.get(VERIFICATION_COOKIE_NAME)
        logger.info(f"function: {func.__name__}, token: {token}")
        if token is None or token != localConfig.LOGIN_PASSWD:
            return makeFailedResponse("verification failed")
        return func(*args, **kwargs)

    return wrapper


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


@app.route("/options", methods=["GET"])
def getOptions():
    """获取所有选项"""
    logger.info(f"get options: {request.args}")
    p = request.args.get("p")
    if p is None:
        return makeFailedResponse("missing arguments")

    if p == 'ledger':
        return jsonify(ledgerOptions.getList())
    elif p == 'time':
        return jsonify(timeOptions.getList())
    else:
        return makeFailedResponse("invalid arguments")


@app.route("/tags", methods=["GET"])
def getTags():
    """获取所有标签"""
    logger.info(f"get tags: {request.args}")
    p = request.args.get("p")
    if p is None:
        return makeFailedResponse("missing arguments")

    if p == 'ledger':
        return sql.getTags(1)
    elif p == 'time':
        return sql.getTags(2)
    else:
        return makeFailedResponse("invalid arguments")


@app.route("/add/ledger", methods=["POST"])
@verifyToken
def addLedger():
    """记录"""
    logger.info(f"add ledger: {request.json}")
    choice = request.json.get("choice")
    amount = request.json.get("amount")
    tags = request.json.get("tags")
    comment = request.json.get("comment")
    if choice is None or amount is None or tags is None or comment is None:
        return makeFailedResponse("missing arguments")
    choice = str(choice)
    if len(choice) != DEF_CHOICE_LENGTH or choice == DEF_DEFAULT * DEF_CHOICE_LENGTH \
            or ledgerOptions.getChild(choice.strip(DEF_DEFAULT)) is not None:
        return makeFailedResponse("invalid choice")
    if amount == '':
        return makeFailedResponse("invalid amount")

    sql.insertLedger(choice, amount, tags, comment)
    return makeSuccessResponse()


@app.route("/get/ledger", methods=["GET"])
def getLedger():
    """获取记录"""
    logger.info(f"get ledger: {request.args}")
    status = request.args.get("status")
    if status is None or not 1 <= int(status) <= 3:
        return makeFailedResponse("invalid status")
    status = int(status)
    ledgers = sql.getLedger(status)
    ret = []
    for ledger in ledgers:
        ret.append([
            datetime.strftime(ledger[0], "%m%d%H"),
            ledger[1].split(DEF_DEFAULT)[0],  # 去掉占位符
            str(ledger[2]).rstrip('0').rstrip('.'),  # 去掉多余的0和小数点
            ledger[3],
            ledger[4],
        ])
    return jsonify(ret)


@app.route("/add/time", methods=["POST"])
def addTime():
    """记录时间"""
    logger.info(f"add time: {request.json}")
    action = request.json.get("action")
    choice = request.json.get("choice")
    time = request.json.get("time")
    tags = request.json.get("tags")
    comment = request.json.get("comment")
    if action is None or choice is None or time is None or tags is None or comment is None:
        return makeFailedResponse("missing arguments")
    if len(choice) != DEF_CHOICE_LENGTH or \
            (choice != DEF_DEFAULT * DEF_CHOICE_LENGTH and timeOptions.getChild(choice.strip(DEF_DEFAULT)) is not None):
        # 注意这里允许默认选项
        return makeFailedResponse("invalid choice")
    time = timeStrToDateObj(time)
    if time is None:
        return makeFailedResponse("invalid time")

    def writeToTxt(statusRec: str, record: list[str]):
        assert statusRec in ['open', 'close'] and len(record) == 4
        with open("log/preTime.txt", "w") as fw:
            fw.write(statusRec + "\n")
            fw.write("\n".join(record))

    # 读取先前的时间记录
    try:
        f = open("log/preTime.txt", "r")
    except FileNotFoundError:
        # 第一次记录时间
        writeToTxt('open', [choice, time.strftime("%d%H%M"), tags, comment])
        return makeSuccessResponse()
    else:
        content = f.read().split("\n")
        assert len(content) == 5
        status, preChoice, preTime, preTags, preComment = content
        preTime = timeStrToDateObj(preTime)
        f.close()
    if time <= preTime:
        return makeFailedResponse("invalid time")

    # 进行逻辑处理与sql插入
    if status == 'open':
        if action == 'start':
            sql.insertTime(preChoice, preTime, time, preTags, preComment)
        elif action == 'break':
            sql.insertTime(preChoice, preTime, time, preTags, preComment)
        elif action == 'end':
            sql.insertTime(choice, preTime, time, tags, comment)
        else:
            return makeFailedResponse("fatal error: invalid action")
    elif status == 'close':
        if action == 'start':
            if preTime < time - timedelta(minutes=5):
                print(preTime, time - timedelta(minutes=5))
                return makeFailedResponse("时间间隔过长")
            time = preTime
        elif action == 'break':
            return makeFailedResponse("invalid action")
        elif action == 'end':
            sql.insertTime(choice, preTime, time, tags, comment)
        else:
            return makeFailedResponse("fatal error: invalid action")
    else:
        raise ValueError(f"Invalid status: {status}")

    nowStatus = 'open' if action == 'start' else 'close'
    writeToTxt(nowStatus, [choice, time.strftime('%d%H%M'), tags, comment])
    return makeSuccessResponse()


@app.route("/get/time", methods=["GET"])
def getTime():
    """获取记录"""
    logger.info(f"get time: {request.args}")
    status = request.args.get("status")
    if status is None:
        return makeFailedResponse("invalid status")

    # 读取某一天的记录
    if len(status) == 6:
        date = datetime.strptime(status, "%y%m%d")
        if date is None:
            return makeFailedResponse("invalid date")
        res = sql.getTimeInDay(date)
        from collections import defaultdict
        counter = defaultdict(int)
        for row in res:
            startTime: datetime
            endTime: datetime
            startTime, endTime, types = row
            if startTime.date() < date.date():
                startTime = date
            if endTime.date() > date.date():
                endTime = date + timedelta(days=1)
            # 统计分钟数, 只统计第一个大类
            counter[types[0]] += (endTime - startTime).seconds // 60
        ret = [{"name": timeOptions.getName(k), "value": f"{v / 60:.1f}"} for k, v in counter.items()]
        return jsonify(ret)

    # 读取当天的记录
    status = int(status)
    res = sql.getTime(1)  # 仅回复当天记录
    ret = []

    # 读取并返回当前时间记录状态
    try:
        with open("log/preTime.txt", "r") as f:
            content = f.read().split("\n")
            assert len(content) == 5
            status, preChoice, preTime, preTags, preComment = content
            ret.append([
                preTime,
                status,
                preChoice.strip(DEF_DEFAULT),
                preTags,
                preComment,
            ])
    except FileNotFoundError:
        pass

    for row in res:
        ret.append([
            datetime.strftime(row[0], "%d%H%M"),
            datetime.strftime(row[1], "%d%H%M"),
            row[2].split(DEF_DEFAULT)[0],  # 去掉占位符
            row[3],
            row[4],
        ])
    return jsonify(ret)


app.run(localConfig.APP_HOST, localConfig.APP_PORT, ssl_context=(localConfig.SSL_CRT, localConfig.SSL_KEY))
sql.close()
