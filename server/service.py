from flask import Request, Response, jsonify
from request_dtos import *
from google import genai


def directly_called_account_action(request: Request) -> Response:
    obj: BalanceActionDTO = BalanceActionDTO.fromJson(request.get_json())
    return jsonify(_directly_called_account_action(obj).toJson())


def _directly_called_account_action(obj: BalanceActionDTO) -> BalanceActionResponseDTO:
    result: tuple[BalanceActionError, Amount]

    if obj.action == BalanceAction.withdrawal:
        result = _withdrawal(obj.amount, obj.balance)
    elif obj.action == BalanceAction.deposit:
        result = _deposit(obj.amount, obj.balance)

    return BalanceActionResponseDTO(not result[0].hasError(), result[0], result[1])


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
FUNCTION_NAME_NO_FUNCTION_CALLED = "no_function_called"

PROMPT_FOR_FUNCTION = f"""
You have access to a variety of hidden functional tools and must decide which, if any, to call.
First, a function which deposits money into a users bank account named {FUNCTION_NAME_DEPOSIT}; this function accepts two integer arguments: first dollars and second cents which should be printed in that order.
Second a function to withdraw money from a users bank account named {FUNCTION_NAME_WITHDRAWAL}; this function accepts two integer arguments: first dollars and second cents which should be printed in that order.
Use the given input to determine which of these functions, if any, you should call.
If you decide to call a function respond with the exact name of the function followed by a space and its arguments.
Function arguments should be printed in a comma-separated ordered list, do not surround the argument list with parenthesis or brackets.
If no function should be called, which should be the case unless very clearly indicated, respond with whatever output seems appropriate to best aid the user based on the instruction context given in this prompt and preface your response with {FUNCTION_NAME_NO_FUNCTION_CALLED}.
If the user seems frustrated or angry respond with {FUNCTION_NAME_ESCALATE}.
If the user seems confused or to be asking for guidance respond with {FUNCTION_NAME_HELP}.
The given input is: "*user_input*"
"""

HELP_RESPONSE = """Hmm, it seems like we couldn't understand what you wanted to do.  You can withdraw money or deposit money here.  If you ask to withdraw or deposit money, please include the exact amount you wish to withdraw or deposit in your request."""

MISSING_INFORMATION_RESPONSE = """Seems like we didn't get enough information to complete your request.  Please make sure to include the dollar and cent amounts you wish to withdraw or deposit from / to your account."""

ERROR_DURING_ACCOUNT_ACTION = """It looks like an error occurred, please check the on screen message and correct your request."""

ESCALATE_RESPONSE = """We're sorry this isn't working out for you.  If you would like to speak to a customer service representative please call us at 1-800-800-8000."""

WITHDRAWAL_RESPONSE_WITH_NEW_BALANCE = """Funds withdrawn successfully.  Your new account balance is *dollars* dollars and *cents* cents.  Have a wonderful day!"""

DEPOSIT_RESPONSE_WITH_NEW_BALANCE = """Funds deposited successfully.  Your new account balance is *dollars* dollars and *cents* cents.  Have a wonderful day!"""

model = "gemini-2.5-flash"


def prompted_account_action(request: Request) -> Response:
    obj: BalancePromptActionDTO = BalancePromptActionDTO.fromJson(request.get_json())

    client = genai.Client()
    initial_response = _send_initial_prompt(obj.prompt, client)
    print("Got back from LLM: ", initial_response)

    if FUNCTION_NAME_NO_FUNCTION_CALLED in initial_response:
        return jsonify(
            BalancePromptActionResponseDTO(
                False,
                False,
                initial_response.replace(FUNCTION_NAME_NO_FUNCTION_CALLED, ""),
                Amount.empty(),
                BalanceActionError.noError(),
            ).toJson()
        )

    parsed = _parse_initial_response(initial_response)

    if len(parsed) < 1 or FUNCTION_NAME_HELP in parsed[0]:
        return jsonify(
            BalancePromptActionResponseDTO(
                False,
                False,
                HELP_RESPONSE,
                Amount.empty(),
                BalanceActionError.noError(),
            ).toJson()
        )
    elif FUNCTION_NAME_ESCALATE in parsed[0]:
        return jsonify(
            BalancePromptActionResponseDTO(
                False,
                True,
                ESCALATE_RESPONSE,
                Amount.empty(),
                BalanceActionError.noError(),
            ).toJson()
        )
    elif len(parsed) != 3:
        return jsonify(
            BalancePromptActionResponseDTO(
                False,
                False,
                MISSING_INFORMATION_RESPONSE,
                Amount.empty(),
                BalanceActionError.noError(),
            ).toJson()
        )

    function_deposit = FUNCTION_NAME_DEPOSIT in parsed[0]
    function_withdrawal = FUNCTION_NAME_WITHDRAWAL in parsed[0]
    if not (function_deposit or function_withdrawal):
        return jsonify(
            BalancePromptActionResponseDTO(
                False,
                False,
                HELP_RESPONSE,
                Amount.empty(),
                BalanceActionError.noError(),
            ).toJson()
        )

    balance_action_dto = BalanceActionDTO(
        BalanceAction.deposit if function_deposit else BalanceAction.withdrawal,
        obj.balance,
        Amount(int(parsed[1]), int(parsed[2])),
    )

    response = _directly_called_account_action(balance_action_dto)
    if response.error.hasError():
        return jsonify(
            BalancePromptActionResponseDTO(
                False,
                False,
                ERROR_DURING_ACCOUNT_ACTION,
                Amount.empty(),
                response.error,
            ).toJson()
        )

    return jsonify(
        BalancePromptActionResponseDTO(
            True,
            False,
            (
                _set_balance_on_response_message(
                    (
                        WITHDRAWAL_RESPONSE_WITH_NEW_BALANCE
                        if function_withdrawal
                        else DEPOSIT_RESPONSE_WITH_NEW_BALANCE
                    ),
                    response.balance,
                )
            ),
            response.balance,
            response.error,
        ).toJson()
    )


def _set_balance_on_response_message(response: str, balance: Amount) -> str:
    return response.replace("*dollars*", str(balance.dollars)).replace(
        "*cents*", str(balance.cents)
    )


def _parse_initial_response(response: str) -> list[str]:
    space_removed = response.split(" ")
    final_split = []

    for arg in space_removed:
        comma_split = arg.split(",")
        if len(comma_split) == 1:
            final_split.append(arg)
        else:
            final_split.extend(comma_split)

    return list(filter(lambda elem: elem and not elem.isspace(), final_split))


def _send_initial_prompt(prompt: str, client: genai.Client) -> str:
    response = client.models.generate_content(
        model=model,
        contents=PROMPT_FOR_FUNCTION.replace("*user_input*", prompt),
    )
    return response.text
