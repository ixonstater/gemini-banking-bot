export type BalanceAction = "DEPOSIT" | "WITHDRAWAL";

export type Amount = {
  dollars: number;
  cents: number;
};

type BalanceActionDTO = {
  action: BalanceAction;
  amount: Amount;
  balance: Amount;
};

type BalancePromptActionDTO = {
  prompt: string;
  balance: Amount;
};

export function callForNewBalance(
  action: BalanceAction,
  balance: Amount,
  amount: Amount
): Amount {
  return {
    dollars: 0,
    cents: 0,
  };
}

export function callForNewBalanceViaPrompt(
  prompt: string,
  balance: Amount
): Amount {
  return {
    dollars: 0,
    cents: 0,
  };
}
