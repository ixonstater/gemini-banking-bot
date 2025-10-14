import { Send } from "@mui/icons-material";
import {
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  IconButton,
  Snackbar,
  TextField,
} from "@mui/material";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardActions from "@mui/material/CardActions";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import {
  Fragment,
  useState,
  type Dispatch,
  type JSX,
  type SetStateAction,
} from "react";
import {
  callForNewBalance,
  callForNewBalanceViaPrompt,
  type Amount,
  type BalanceAction,
  type BalanceActionError,
} from "../api/GeminiBanking";

type StateFunction<T> = Dispatch<SetStateAction<T>>;

type ErrorSnackState = {
  open: boolean;
  msg: string;
};

const uiMaxWidth = 400;
const uiMinWidth = 275;

export default function OutlinedCard() {
  const [balance, setBalance] = useState<Amount>({ dollars: 0, cents: 0 });

  const [dialogState, setDialogState] = useState<BalanceAction>("WITHDRAWAL");
  const [dialogOpen, setDialogOpen] = useState(false);

  const [errorSnackState, setErrorSnackState] = useState<ErrorSnackState>({
    open: false,
    msg: "",
  });

  return (
    <Fragment>
      <Box sx={{ minWidth: uiMinWidth, maxWidth: uiMaxWidth }}>
        <Card variant="outlined">
          <CardContent>
            <Typography variant="h5" component="div">
              Fund Management
            </Typography>
            <Typography sx={{ color: "text.secondary", mb: 1.5 }}>
              Bank Account Balance
            </Typography>
            <Typography variant="body2">{formatForDollars(balance)}</Typography>
          </CardContent>
          <CardActions>
            <Button
              size="small"
              variant="contained"
              onClick={() => {
                setDialogOpen(true);
                setDialogState("DEPOSIT");
              }}
            >
              Deposit
            </Button>
            <Button
              size="small"
              variant="contained"
              onClick={() => {
                setDialogOpen(true);
                setDialogState("WITHDRAWAL");
              }}
            >
              Withdrawal
            </Button>
          </CardActions>
        </Card>
      </Box>
      <ChatbotEntryField
        setErrorSnackState={setErrorSnackState}
        balance={balance}
        setBalance={setBalance}
      ></ChatbotEntryField>
      <FormDialog
        dialogState={dialogState}
        dialogOpen={dialogOpen}
        setDialogOpen={setDialogOpen}
        submit={async (amount) => {
          const newBalance = await callForNewBalance({
            action: dialogState as BalanceAction,
            balance,
            amount,
          });

          if (!newBalance.success) {
            openErrorSnackBar(setErrorSnackState, newBalance.error);
            return;
          }

          setBalance(newBalance.balance);
        }}
      ></FormDialog>
      <ErrorSnackBar state={errorSnackState}></ErrorSnackBar>
    </Fragment>
  );
}

function openErrorSnackBar(
  setErrorSnackState: StateFunction<ErrorSnackState>,
  error: BalanceActionError,
  delay: number = 7000
) {
  setErrorSnackState({
    open: true,
    msg: getErrorMessageFromErrorType(error),
  });

  setTimeout(() => setErrorSnackState({ open: false, msg: "" }), delay);
}

function getErrorMessageFromErrorType(error: BalanceActionError): string {
  switch (error) {
    case "INSUFFICIENT_FUNDS":
      return "Insufficient funds for withdrawal amount.";
    case "NEGATIVE_BALANCE":
      return "Negative balance given, contact customer service for help.";
    case "NEGATIVE_DEPOSIT_AMOUNT":
      return "Negative transfer amount given, dollars and cents must be positive.";
    default:
      return "";
  }
}

function formatForDollars(amount: Amount): string {
  const usdFormatter = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  });

  return usdFormatter.format(amount.dollars + amount.cents / 100);
}

function FormDialog({
  dialogState,
  dialogOpen,
  setDialogOpen,
  submit,
}: {
  dialogState: BalanceAction;
  dialogOpen: boolean;
  setDialogOpen: StateFunction<boolean>;
  submit: (amount: Amount) => void;
}) {
  let [dollars, cents] = [0, 0];

  return (
    <Fragment>
      <Dialog
        sx={{ maxWidth: 450 }}
        open={dialogOpen}
        onClose={() => {
          setDialogOpen(false);
        }}
      >
        <DialogTitle>{getDialogTitle(dialogState)}</DialogTitle>
        <DialogContent>
          <DialogContentText>{getDialogContent(dialogState)}</DialogContentText>
          <Box sx={{ display: "flex", flexDirection: "column", maxWidth: 250 }}>
            <TextField
              autoFocus
              required
              margin="dense"
              name="dollars"
              label="Dollars"
              type="number"
              variant="standard"
              onChange={(event) => (dollars = parseInt(event.target.value))}
            />
            <TextField
              autoFocus
              required
              margin="dense"
              name="cents"
              label="Cents"
              type="number"
              variant="standard"
              onChange={(event) => (cents = parseInt(event.target.value))}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button
            variant="outlined"
            onClick={() => {
              setDialogOpen(false);
            }}
          >
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={() => {
              setDialogOpen(false);
              submit({ dollars, cents });
            }}
          >
            Confirm
          </Button>
        </DialogActions>
      </Dialog>
    </Fragment>
  );
}

function getDialogTitle(state: BalanceAction): string {
  if (state === "DEPOSIT") {
    return "Deposit";
  } else if (state === "WITHDRAWAL") {
    return "Withdrawal";
  }

  return "";
}

function getDialogContent(state: BalanceAction): string {
  if (state === "DEPOSIT") {
    return "Please enter the amount you would like to deposit in dollars and cents.";
  } else if (state === "WITHDRAWAL") {
    return "Please enter the amount you would like to withdrawal in dollars and cents.";
  }

  return "";
}

function ChatbotEntryField({
  balance,
  setBalance,
  setErrorSnackState,
}: {
  balance: Amount;
  setBalance: StateFunction<Amount>;
  setErrorSnackState: StateFunction<ErrorSnackState>;
}): JSX.Element {
  const [chatResponse, setChatResponse] = useState("");
  const [escalateUser, setEscalateUser] = useState(false);
  let prompt = "";

  return (
    <>
      <Box
        sx={{
          minWidth: uiMinWidth,
          maxWidth: uiMaxWidth,
          marginTop: 4,
          display: "flex",
          flexDirection: "column",
        }}
      >
        <Typography sx={{ marginLeft: 2 }} variant="h5">
          Bank Chatbot
        </Typography>
        <Box sx={{ display: "flex" }}>
          <TextField
            onChange={(event) => {
              prompt = event.target.value;
            }}
            label="Try asking me to withdraw money."
            sx={{ flexGrow: 1 }}
          ></TextField>
          <IconButton
            onClick={async () => {
              const response = await callForNewBalanceViaPrompt({
                prompt,
                balance,
              });

              setChatResponse(response.response);

              if (response.success) {
                setBalance(response.balance);
                return;
              }

              if (response.balanceActionError != "NO_ERROR") {
                openErrorSnackBar(
                  setErrorSnackState,
                  response.balanceActionError,
                  20000
                );
              }

              if (response.escalateUser) {
                setEscalateUser(true);
              }
            }}
          >
            <Send></Send>
          </IconButton>
        </Box>
        {escalateUser ? (
          <Button
            sx={{ marginTop: 2 }}
            size="small"
            variant="contained"
            onClick={() => alert("This button does nothing important.")}
          >
            Chat with a human
          </Button>
        ) : null}
        <Box
          sx={{
            minWidth: uiMinWidth,
            maxWidth: uiMaxWidth,
            marginTop: 2,
            border: "1px solid rgba(0, 0, 0, 0.12)",
            borderRadius: "4px",
            minHeight: 250,
            padding: 2,
          }}
        >
          <Typography>{chatResponse}</Typography>
        </Box>
      </Box>
    </>
  );
}

function ErrorSnackBar({ state }: { state: ErrorSnackState }): JSX.Element {
  return (
    <Snackbar
      anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      open={state.open}
      message={state.msg}
    />
  );
}
