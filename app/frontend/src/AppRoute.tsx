import { Container, makeStyles } from "@material-ui/core";
import React, { useEffect } from "react";
import { Redirect, Route, RouteProps } from "react-router-dom";

import Navigation from "./components/Navigation";
import { useAuthContext } from "./features/auth/AuthProvider";
import { jailRoute, loginRoute } from "./routes";

const useStyles = makeStyles((theme) => ({
  standardContainer: {
    paddingBottom: theme.shape.navPaddingMobile,
    paddingLeft: theme.spacing(2),
    paddingRight: theme.spacing(2),
    [theme.breakpoints.up("md")]: {
      paddingBottom: 0,
      paddingTop: theme.shape.navPaddingDesktop,
    },
  },
  fullscreenContainer: {
    padding: 0,
    margin: "0 auto",
  },
}));

interface AppRouteProps extends RouteProps {
  isPrivate: boolean;
  isFullscreen?: boolean;
}

export default function AppRoute({
  children,
  isPrivate,
  isFullscreen = false,
  ...otherProps
}: AppRouteProps) {
  const { authState, authActions } = useAuthContext();
  const isAuthenticated = authState.authenticated;
  const isJailed = authState.jailed;
  useEffect(() => {
    if (!isAuthenticated && isPrivate) {
      authActions.authError("Please log in.");
    }
  });

  const classes = useStyles();

  return isPrivate ? (
    <Route
      {...otherProps}
      render={({ location }) => (
        <>
          {isAuthenticated ? (
            <Container maxWidth="md" className={classes.standardContainer}>
              {isJailed ? (
                <Redirect to={jailRoute} />
              ) : (
                <>
                  <Navigation />
                  {children}
                </>
              )}
            </Container>
          ) : (
            <Redirect
              to={{
                pathname: loginRoute,
                state: { from: location },
              }}
            />
          )}
        </>
      )}
    />
  ) : (
    <>
      {isFullscreen ? (
        <Container maxWidth="md" className={classes.fullscreenContainer}>
          <Route {...otherProps} render={() => children} />
        </Container>
      ) : (
        <Container maxWidth="md" className={classes.standardContainer}>
          <Navigation />
          <Route {...otherProps} render={() => children} />
        </Container>
      )}
    </>
  );
}
