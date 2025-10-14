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

type BalancePromptActionResponseDTO = {
  balance: Amount;
  balanceActionError: BalanceActionError;
  escalateUser: boolean;
  response: string;
  success: boolean;
};

type BalanceActionResponseDTO = {
  success: boolean;
  error: BalanceActionError;
  balance: Amount;
};

export type BalanceActionError =
  | "NO_ERROR"
  | "INSUFFICIENT_FUNDS"
  | "NEGATIVE_DEPOSIT_AMOUNT"
  | "NEGATIVE_BALANCE";

export async function callForNewBalance(
  body: BalanceActionDTO
): Promise<BalanceActionResponseDTO> {
  const response = await fetch("/api/account/action", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  const json = await response.json();

  return json;
}

export async function callForNewBalanceViaPrompt(
  body: BalancePromptActionDTO
): Promise<BalancePromptActionResponseDTO> {
  const response = await fetch("/api/account/prompt", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  const json = await response.json();

  return json;
}
