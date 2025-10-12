class Amount:
    dollars: int = 0
    cents: int = 0

    def __init__(self, dollars: int, cents: int):
        self.dollars = dollars
        self.cents = cents


class BalanceAction:
    withdrawal = "WITHDRAWAL"
    deposit = "DEPOSIT"


class BalanceActionError:
    insufficientFunds = "INSUFFICIENT_FUNDS"


class BalanceActionDTO:
    action: str
    balance: Amount
    amount: Amount

    def fromJsonDict(dict: dict[str, object]):
        pass


class BalanceActionResponseDTO:
    success: bool
    error: BalanceActionError
    balance: Amount

    def __init__(self, success: bool, error: BalanceActionError, balance: Amount):
        self.success = success
        self.error = error
        self.balance = balance

    def toJsonDict(self) -> dict[str, object]:
        pass


class BalancePromptActionDTO:
    prompt: str
    balance: Amount

    def fromJsonDict(dict: dict[str, object]):
        pass


class BalancePromptActionResponseDTO:
    response: str
    success: bool
    balance: Amount

    def __init__(self, success: bool, response: str, balance: Amount):
        self.response = response
        self.success = success
        self.balance = balance

    def toJsonDict(self) -> dict[str, object]:
        pass
