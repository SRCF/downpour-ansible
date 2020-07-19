# Overview

This establishes bridges between

  mattermost <-> matrix <-> irc

using matrix-appservice-slack and matrix-appservice-irc. At the moment, the
role is slightly faulty --- systemd services aren't restarted at the right
time, or future tasks run before the systemd services finish starting back up.
nginx seems prone to get killed during this process. The solution is that
whenever ansible fails, make sure the services that should be up by the time
are indeed up. Then restart ansible. Rinse and repeat.

The matrix <-> irc setup is full automated via ansible, and is configured by
the `matrix_irc_bridges` variable. The matrix <-> slack setup requires some
manual intervention.

For each matrix room you want to bridge mattermost to, add the matrix room name
in `matrix_mattermost_bridges`. This joins `slackbot` to the rooms and gives it
the right privileges. To actually link up the channels, we need to run the
linking command in the `#slackbot-admin` matrix channel. You will have to be a
team administrator of the Mattermost channel.

You should join `matrix.srcf.net` (or your corresponding matrix domain) as user
`botmaster`. The password is placed in `/root/matrix-botmaster-password` on
the remote host. One can use the offical web client on https://app.element.io/
to do so. You are already a member of `#slackbot-admin`.

To link a channel, we need to type

```
link --room <room_id> --channel_id <channel_id> --webhook_url <webhook_url>
```
The parameters are obtained as follows:

 * `room_id` is the id of the matrix room we want to bridge to. This is a long,
   opaque name, not to be confused with the alias (e.g.
   `#slackbot-admin:matrix.srcf.net` is an alias. The room id is something like
   `!IyciLDVRnkISZWktsv:matrix.srcf.net`). On Element, this can be read from
   the "Advanced" setting tab of the room.
 * `channel_id` is the Mattermost channel id. On our set up, you can obtain
   this by typing the `/channel_id` command in the mattermost channel
 * `webhook_url` is obtained by performing the following procedure in
   Mattermost: there is a hamburger on the left-hand bar. In the menu, click
   "Integrations", then go to "Incoming Webhooks". There, click "Add Incoming
   Webhook". Set the channel to the Mattermost channel you want to bridge, and
   give it a descriptive title. All other fields can be left blank (you may
   want to lock the webhook to the specified channel). Then click save. You are
   then given a webhook url.

Once the command is run, slackbot should reply with something of the form
```
Room is now pending-name
Inbound URL is http://127.0.0.1:9898/...
```
Copy the URL. Go back to the Mattermost integrations page and select `Outgoing
webhooks` this time. Add an outgoing webhook, set a title, restricting to the
right channel, and paste the URL from Slackbot into "Callback URLs". Then save.
All other fields can be blank.

The bridge should be working now.
