from flask import Request, Response, jsonify
from request_dtos import *
from google import genai


def directly_called_account_action(request: Request) -> Response:
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


FUNCTION_NAME_DEPOSIT = "deposit_money"
FUNCTION_NAME_WITHDRAWAL = "withdraw_money"
FUNCTION_NAME_ESCALATE = "escalate_user"
FUNCTION_NAME_HELP = "help_requested"

PROMPT_FOR_FUNCTION = f"""
You have access to a variety of hidden functional tools and must decide which, if any, to call.
First, a function which deposits money into a users bank account named {FUNCTION_NAME_DEPOSIT}; this function accepts two integer arguments: first dollars and second cents which should be printed in that order.
Second a function to withdraw money from a users bank account named {FUNCTION_NAME_WITHDRAWAL}; this function accepts two integer arguments: first dollars and second cents which should be printed in that order.
Use the given input to determine which of these functions, if any, you should call.
If you decide to call a function respond with the exact name of the function followed by a space and its arguments.
Function arguments should be printed in a comma-separated ordered list, do not surround the argument list with parenthesis or brackets.
If no function should be called, which should be the case unless very clearly indicated, respond with no_function_called.
If the user seems frustrated or angry respond with {FUNCTION_NAME_ESCALATE}.
If the user seems confused or to be asking for guidance respond with {FUNCTION_NAME_HELP}.
The given input is: "*user_input*"
"""

WITHDRAWAL_RESPONSE_WITH_NEW_BALANCE = """
Funds withdrawn successfully.  Your new account balance is *dollars* dollars and *cents* cents.  Have a wonderful day!
"""

DEPOSIT_RESPONSE_WITH_NEW_BALANCE = """
Funds deposited successfully.  Your new account balance is *dollars* dollars and *cents* cents.  Have a wonderful day!
"""

model = "gemini-2.5-flash"


def prompted_account_action(request: Request) -> Response:
    obj: BalancePromptActionDTO = BalancePromptActionDTO.fromJson(request.get_json())

    client = genai.Client()
    initial_response = _send_initial_prompt(obj.prompt, client)

    return jsonify({"response": initial_response})


def _send_initial_prompt(prompt: str, client: genai.Client) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=PROMPT_FOR_FUNCTION.replace("*user_input*", prompt),
    )
    return response.text
