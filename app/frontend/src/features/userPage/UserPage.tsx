import { Grid, makeStyles, Typography } from "@material-ui/core";
import { TabContext, TabPanel } from "@material-ui/lab";
import React from "react";
import { Link, useParams } from "react-router-dom";

import Alert from "../../components/Alert";
import Button from "../../components/Button";
import CircularProgress from "../../components/CircularProgress";
import { CouchIcon, EditIcon } from "../../components/Icons";
import TabBar from "../../components/TabBar";
import TextBody from "../../components/TextBody";
import { User } from "../../pb/api_pb";
import { profileRoute, routeToNewHostRequest } from "../../routes";
import { useIsMounted, useSafeState } from "../../utils/hooks";
import AddFriendButton from "../connections/friends/AddFriendButton";
import useCurrentUser from "../userQueries/useCurrentUser";
import useUserByUsername from "../userQueries/useUserByUsername";
import UserAbout from "./UserAbout";
import UserGuestbook from "./UserGuestbook";
import UserHeader from "./UserHeader";
import UserPlace from "./UserPlace";
import UserSection from "./UserSection";
import UserSummary from "./UserSummary";

const useStyles = makeStyles((theme) => ({
  actionButton: {
    marginBottom: theme.spacing(2),
  },
  tabPanel: {
    padding: 0,
  },
}));

const userPageTabLabels = {
  aboutMe: <Typography variant="body2">About me</Typography>,
  myHome: <Typography variant="body2">My Home</Typography>,
  references: <Typography variant="body2">References</Typography>,
  // favourites: <Typography variant="body2">Favourites</Typography>,
  // photos: <Typography variant="body2">Photos</Typography>,
};

export default function UserPage() {
  const classes = useStyles();
  const { username } = useParams<{ username: string }>();
  const { data: user, isLoading, isError, error } = useUserByUsername(
    username,
    true
  );
  const isMounted = useIsMounted();
  const [currentUserPageTab, setCurrentUserPageTab] = useSafeState<
    keyof typeof userPageTabLabels
  >(isMounted, "aboutMe");
  const [mutationError, setMutationError] = useSafeState(isMounted, "");
  const isCurrentUser = useCurrentUser().data?.userId === user?.userId;

  return (
    <>
      {mutationError ? <Alert severity="error">{mutationError}</Alert> : null}
      {isError ? (
        <Alert severity="error">{error}</Alert>
      ) : isLoading ? (
        <CircularProgress />
      ) : (
        user && (
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={4}>
              <UserHeader user={user}>
                {isCurrentUser ? (
                  <Button
                    startIcon={<EditIcon />}
                    component={Link}
                    to={profileRoute}
                    className={classes.actionButton}
                  >
                    Edit your profile
                  </Button>
                ) : user.friends === User.FriendshipStatus.NOT_FRIENDS ? (
                  <AddFriendButton
                    userId={user.userId}
                    setMutationError={setMutationError}
                  />
                ) : user.friends === User.FriendshipStatus.PENDING ? (
                  <TextBody className={classes.actionButton}>
                    Pending friend request...
                  </TextBody>
                ) : null}
                {!isCurrentUser && (
                  <Button
                    startIcon={<CouchIcon />}
                    component={Link}
                    to={routeToNewHostRequest(user.userId)}
                    className={classes.actionButton}
                  >
                    Request to stay
                  </Button>
                )}
              </UserHeader>
              <UserSummary user={user} />
            </Grid>
            <Grid item xs={12} sm={6} md={8}>
              <TabContext value={currentUserPageTab}>
                <TabBar
                  labels={userPageTabLabels}
                  value={currentUserPageTab}
                  setValue={setCurrentUserPageTab}
                />
                <TabPanel classes={{ root: classes.tabPanel }} value="aboutMe">
                  <UserSection title="Overview">
                    <UserAbout user={user} />
                  </UserSection>
                </TabPanel>
                <TabPanel classes={{ root: classes.tabPanel }} value="myHome">
                  <UserSection title="My Place">
                    <UserPlace user={user} />
                  </UserSection>
                </TabPanel>
                <TabPanel
                  classes={{ root: classes.tabPanel }}
                  value="references"
                >
                  <UserSection title="Guestbook">
                    <UserGuestbook user={user} />
                  </UserSection>
                </TabPanel>
                {/* <TabPanel value="favourites">
                  Coming soon...
                </TabPanel>
                <TabPanel value="photos">
                  Coming soon...
                </TabPanel> */}
              </TabContext>
            </Grid>
          </Grid>
        )
      )}
    </>
  );
}
