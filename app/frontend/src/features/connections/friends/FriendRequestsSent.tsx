import {
  Box,
  Card,
  CircularProgress,
  makeStyles,
  Typography,
} from "@material-ui/core";
import React from "react";
import Alert from "../../../components/Alert";
import { useIsMounted, useSafeState } from "../../../utils/hooks";
import useFriendsBaseStyles from "./useFriendsBaseStyles";

const useStyles = makeStyles({
  root: {},
});

function FriendRequestsSent() {
  const baseClasses = useFriendsBaseStyles();
  const isMounted = useIsMounted();
  const [errorMessage] = useSafeState(isMounted, "");
  const [loading] = useSafeState(isMounted, false);

  return (
    <Card>
      <Box>
        <Typography className={baseClasses.header} variant="h2">
          Friend requests you sent
        </Typography>
        {loading ? (
          <CircularProgress className={baseClasses.circularProgress} />
        ) : errorMessage ? (
          <Alert className={baseClasses.errorAlert} severity="error">
            {errorMessage}
          </Alert>
        ) : null}
      </Box>
    </Card>
  );
}

export default FriendRequestsSent;