# zfs-status-to-discord

A little project built to deliver nicely formatted reports on the state of your
`zfs` storage pool to a Discord server.

<p align="center">
  <img src="zfsHealthy.png" width=70% />
  <br>
  <img src="zfsUnhealthy.png" width=70% />
<br>
<ins><b><i>Healthy and unhealthy examples, respectively</i></b></ins>
</p>

## Getting started

Copy the [raw
code](https://raw.githubusercontent.com/rdvm/zfs-status-to-discord/main/main.py)
of `main.py` and create your own `main.py` file on your server. If you'd
like to execute by name from anywhere, make sure that the file is somewhere in
your `$PATH`. Make the file executable by running

```sh
chmod +x main.py
```

This file assumes the existence of a `config.py` containing your Discord
webhook URL(s). You can look at the included `example.config.py` as a
reference. Make sure it is in the same directory as `main.py`.

> **Note**
> I wanted the message to be routed to a different channel when there was an
> unhealthy state detected, so I have two webhooks in my file, but you can use
> the same webhook for both variables if you want the messages to always go to
> one channel.

If you're not sure how to make and use Discord webhooks, you can check out
[this intro to Discord webhooks documentation](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks#making-a-webhook).

## Goals/rationale

I use various channels in a Discord server to receive notifications from
systems and services. I wanted scheduled summary reports of my `zfs` storage
pool on a Debian server, and I also was looking for a little Python project, so
I decided this was a good target.

The output of `zpool status` gives a nice overview of your storage pool(s), but
it's one big string with a lot of whitespace to make the output look like a
table. So the idea was to parse the text both to facilitate shipping the output
to Discord and also to enable dynamic message content and routing based on the
contents of the text.

Since this is meant to be run on a server where I don't want any more packages
or services than necessary, I only used built-in Python modules and tested with
Python `3.9.2`, since that's the default version on Debian 11 right now. I also
wanted to keep everything in one file to make this as simple/portable as
possible. (The separate `config.py` was necessary to keep my webhook URLs off
the internet 😎)
