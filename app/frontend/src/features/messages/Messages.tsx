import * as React from "react";
import { Route, Switch, useHistory, useParams } from "react-router-dom";

import { messagesRoute } from "../../AppRoutes";
import NotificationBadge from "../../components/NotificationBadge";
import PageTitle from "../../components/PageTitle";
import TabBar from "../../components/TabBar";
import useNotifications from "../useNotifications";
import GroupChatsTab from "./groupchats/GroupChatsTab";
import GroupChatView from "./groupchats/GroupChatView";
import HostRequestView from "./surfing/HostRequestView";
import NewHostRequest from "./surfing/NewHostRequest";
import SurfingTab from "./surfing/SurfingTab";

export function MessagesNotification() {
  const { data } = useNotifications();

  return (
    <NotificationBadge count={data?.unseenMessageCount}>
      Group Chats
    </NotificationBadge>
  );
}

export function HostRequestsReceivedNotification() {
  const { data } = useNotifications();

  return (
    <NotificationBadge count={data?.unseenReceivedHostRequestCount}>
      Hosting
    </NotificationBadge>
  );
}

export function HostRequestsSentNotification() {
  const { data } = useNotifications();

  return (
    <NotificationBadge count={data?.unseenSentHostRequestCount}>
      Surfing
    </NotificationBadge>
  );
}

const labels = {
  //all: "All",
  groupchats: <MessagesNotification />,
  hosting: <HostRequestsReceivedNotification />,
  surfing: <HostRequestsSentNotification />,
  //meet: "Meet",
  //archived: "Archived",
};

type MessageType = keyof typeof labels;

export default function Messages() {
  const history = useHistory();
  const { type = "groupchats" } = useParams<{ type: keyof typeof labels }>();
  const messageType = type in labels ? (type as MessageType) : "groupchats";

  const header = (
    <>
      <PageTitle>Messages</PageTitle>
      <TabBar
        value={messageType}
        setValue={(newType) =>
          history.push(
            `${messagesRoute}/${
              newType !== "groupchats" ? newType : "groupchats"
            }`
          )
        }
        labels={labels}
      />
    </>
  );

  return (
    <>
      <Switch>
        <Route path={`${messagesRoute}/groupchats/:groupChatId`}>
          <GroupChatView />
        </Route>
        <Route path={`${messagesRoute}/groupchats`}>
          {header}
          <GroupChatsTab />
        </Route>
        <Route path={`${messagesRoute}/request/new/:userId`}>
          <NewHostRequest />
        </Route>
        <Route path={`${messagesRoute}/request/:hostRequestId`}>
          <HostRequestView />
        </Route>
        <Route path={`${messagesRoute}/hosting`}>
          {header}
          <SurfingTab type="hosting" />
        </Route>
        <Route path={`${messagesRoute}/surfing`}>
          {header}
          <SurfingTab type="surfing" />
        </Route>
        <Route path={`${messagesRoute}/meet`}>
          {header}
          MEET
        </Route>
        <Route path={`${messagesRoute}/archived`}>
          {header}
          ARCHIVED
        </Route>
        <Route path={`${messagesRoute}/:messageId?`}>
          {header}
          All
        </Route>
      </Switch>
    </>
  );
}
