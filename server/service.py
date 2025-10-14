from flask import Request, jsonify
from request_dtos import *


def directly_called_account_action(request: Request):
    obj: BalanceActionDTO = BalanceActionDTO.fromJsonDict(request.get_json())

    result: tuple[BalanceActionError, Amount]

    if obj.action == BalanceAction.withdrawal:
        result = _withdrawal(obj.amount, obj.balance)
    elif obj.action == BalanceAction.deposit:
        result = _deposit(obj.amount, obj.balance)

    success = result[0] == ""
    return jsonify(BalanceActionResponseDTO(success, result[0], result[1]))


def _withdrawal(amount: Amount, balance: Amount) -> tuple[BalanceActionError, Amount]:
    return (BalanceActionError(), Amount(0, 0))


def _deposit(amount: Amount, balance: Amount) -> tuple[BalanceActionError, Amount]:
    return (BalanceActionError(), Amount(0, 0))
