from typing import Any


class Amount:
    dollars: int = 0
    cents: int = 0

    def __init__(self, dollars: int, cents: int):
        self.dollars = dollars
        self.cents = cents

    @staticmethod
    def empty() -> Amount:
        return Amount(0, 0)

    @staticmethod
    def fromJson(dict: dict[str, Any]) -> Amount:
        return Amount(dict["dollars"], dict["cents"])

    def toJson(self) -> dict[str, Any]:
        return {"dollars": self.dollars, "cents": self.cents}

    def minus(self, amount: Amount):
        dollars: int = self.dollars - amount.dollars
        cents: int = self.cents - amount.cents

        if cents < 0:
            cents = 100 - abs(cents)
            dollars -= 1

        return Amount(dollars, cents)


class BalanceAction:
    withdrawal = "WITHDRAWAL"
    deposit = "DEPOSIT"


class BalanceActionError:
    _error = ""

    def __init__(self, error):
        self._error = error

    def toJson(self) -> str:
        return self._error

    def hasError(self) -> bool:
        return self._error != "NO_ERROR"

    @staticmethod
    def noError() -> BalanceActionError:
        return BalanceActionError("NO_ERROR")

    @staticmethod
    def insufficientFunds() -> BalanceActionError:
        return BalanceActionError("INSUFFICIENT_FUNDS")

    @staticmethod
    def negativeDepositAmount() -> BalanceActionError:
        return BalanceActionError("NEGATIVE_DEPOSIT_AMOUNT")

    @staticmethod
    def negativeBalanceAmount() -> BalanceActionError:
        return BalanceActionError("NEGATIVE_BALANCE")


class BalanceActionDTO:
    action: str
    balance: Amount
    amount: Amount

    def __init__(self, action, balance, amount):
        self.action = action
        self.balance = balance
        self.amount = amount

    @staticmethod
    def fromJson(dict: dict[str, Any]) -> BalanceActionDTO:
        return BalanceActionDTO(
            dict["action"],
            Amount.fromJson(dict["balance"]),
            Amount.fromJson(dict["amount"]),
        )


class BalanceActionResponseDTO:
    success: bool
    error: BalanceActionError
    balance: Amount

    def __init__(self, success: bool, error: BalanceActionError, balance: Amount):
        self.success = success
        self.error = error
        self.balance = balance

    def toJson(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "error": self.error.toJson(),
            "balance": self.balance.toJson(),
        }


class BalancePromptActionDTO:
    prompt: str
    balance: Amount

    def __init__(self, prompt: str, balance: Amount):
        self.prompt = prompt
        self.balance = balance

    @staticmethod
    def fromJson(dict: dict[str, Any]) -> BalancePromptActionDTO:
        return BalancePromptActionDTO(dict["prompt"], dict["balance"])


class BalancePromptActionResponseDTO:
    response: str
    success: bool
    balance: Amount

    def __init__(self, success: bool, response: str, balance: Amount):
        self.response = response
        self.success = success
        self.balance = balance

    def toJson(self) -> dict[str, Any]:
        return {
            "response": self.response,
            "success": self.success,
            "balance": self.balance,
        }
