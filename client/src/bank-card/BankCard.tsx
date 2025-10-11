import {
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  TextField,
} from "@mui/material";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardActions from "@mui/material/CardActions";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import { Fragment, useState, type Dispatch, type SetStateAction } from "react";
import type { Amount, BalanceAction } from "../api/GeminiBanking";

type StateFunction<T> = Dispatch<SetStateAction<T>>;

type DialogStateType = BalanceAction | "CLOSED";

export default function OutlinedCard() {
  const [balance, setBalance] = useState<Amount>({ dollars: 0, cents: 0 });

  const [dialogState, setDialogState] = useState<DialogStateType>("CLOSED");

  return (
    <Fragment>
      <Box sx={{ minWidth: 275, maxWidth: 300 }}>
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
            <Button size="small" onClick={() => setDialogState("DEPOSIT")}>
              Deposit
            </Button>
            <Button size="small" onClick={() => setDialogState("WITHDRAWAL")}>
              Withdrawal
            </Button>
          </CardActions>
        </Card>
      </Box>
      <FormDialog
        dialogState={dialogState}
        submit={(amount) => {
          setDialogState("CLOSED");
          console.log(amount);
        }}
        cancel={() => {
          setDialogState("CLOSED");
        }}
      ></FormDialog>
    </Fragment>
  );
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
  submit,
  cancel,
}: {
  dialogState: DialogStateType;
  submit: (amount: Amount) => void;
  cancel: () => void;
}) {
  let [dollars, cents] = [0, 0];

  return (
    <Fragment>
      <Dialog
        sx={{ maxWidth: 450 }}
        open={dialogState !== "CLOSED"}
        onClose={cancel}
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
          <Button onClick={cancel}>Cancel</Button>
          <Button onClick={() => submit({ dollars, cents })}>Confirm</Button>
        </DialogActions>
      </Dialog>
    </Fragment>
  );
}

function getDialogTitle(state: DialogStateType): string {
  if (state === "DEPOSIT") {
    return "Deposit";
  } else if (state === "WITHDRAWAL") {
    return "Withdrawal";
  }

  return "";
}

function getDialogContent(state: DialogStateType): string {
  if (state === "DEPOSIT") {
    return "Please enter the amount you would like to deposit in dollars and cents.";
  } else if (state === "WITHDRAWAL") {
    return "Please enter the amount you would like to withdrawal in dollars and cents.";
  }

  return "";
}
