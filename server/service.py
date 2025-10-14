from flask import Request, jsonify
from request_dtos import *


def directly_called_account_action(request: Request):
    obj: BalanceActionDTO = BalanceActionDTO.fromJson(request.get_json())

    result: tuple[BalanceActionError, Amount]

    if obj.action == BalanceAction.withdrawal:
        result = _withdrawal(obj.amount, obj.balance)
    elif obj.action == BalanceAction.deposit:
        result = _deposit(obj.amount, obj.balance)

    return jsonify(
        BalanceActionResponseDTO(
            not result[0].hasError(), result[0], result[1]
        ).toJson()
    )


def _withdrawal(amount: Amount, balance: Amount) -> tuple[BalanceActionError, Amount]:
    if amount.cents < 0 or amount.dollars < 0:
        return BalanceActionError.negativeDepositAmount(), Amount.empty()
    elif balance.cents < 0 or balance.dollars < 0:
        return BalanceActionError.negativeBalanceAmount(), Amount.empty()
    elif _is_overdrawn(amount, balance):
        return BalanceActionError.insufficientFunds(), Amount.empty()

    return BalanceActionError.noError(), balance.minus(amount)


def _is_overdrawn(amount: Amount, balance: Amount) -> bool:
    difference: Amount = balance.minus(amount)

    # Due to the logic in the Amount.minus call, cents will always be positive
    return difference.dollars < 0


def _deposit(
    amount: Amount, balance: Amount
) -> tuple[BalanceActionError, Amount | None]:
    if amount.cents < 0 or amount.dollars < 0:
        return BalanceActionError.negativeDepositAmount(), Amount.empty()
    elif balance.cents < 0 or balance.dollars < 0:
        return BalanceActionError.negativeBalanceAmount(), Amount.empty()

    balance.cents += amount.cents
    balance.dollars += amount.dollars

    return BalanceActionError.noError(), balance
