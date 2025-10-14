from typing import Any


class Amount:
    dollars: int = 0
    cents: int = 0

    def __init__(self, dollars: int, cents: int):
        self.dollars = dollars
        self.cents = cents

    @staticmethod
    def fromJsonDict(dict: dict[str, Any]):
        return Amount(dict["dollars"], dict["cents"])


class BalanceAction:
    withdrawal = "WITHDRAWAL"
    deposit = "DEPOSIT"


class BalanceActionError:
    insufficientFunds = "INSUFFICIENT_FUNDS"


class BalanceActionDTO:
    action: str
    balance: Amount
    amount: Amount

    def __init__(self, action, balance, amount):
        self.action = action
        self.balance = balance
        self.amount = amount

    @staticmethod
    def fromJsonDict(dict: dict[str, Any]):
        return BalanceActionDTO(
            dict["action"],
            Amount.fromJsonDict(dict["balance"]),
            Amount.fromJsonDict(dict["amount"]),
        )


class BalanceActionResponseDTO:
    success: bool
    error: BalanceActionError
    balance: Amount

    def __init__(self, success: bool, error: BalanceActionError, balance: Amount):
        self.success = success
        self.error = error
        self.balance = balance

    def toJsonDict(self) -> dict[str, Any]:
        return {"success": self.success, "error": self.error, "balance": self.balance}


class BalancePromptActionDTO:
    prompt: str
    balance: Amount

    @staticmethod
    def fromJsonDict(dict: dict[str, Any]):
        pass


class BalancePromptActionResponseDTO:
    response: str
    success: bool
    balance: Amount

    def __init__(self, success: bool, response: str, balance: Amount):
        self.response = response
        self.success = success
        self.balance = balance

    def toJsonDict(self) -> dict[str, Any]:
        return {
            "response": self.response,
            "success": self.success,
            "balance": self.balance,
        }
