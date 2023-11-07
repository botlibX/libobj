NAME

::

   LIBOBJ - object library


DESCRIPTION

::

   LIBOBJ is a python3 library implementing the 'obj' package. It
   provides all the tools to program a bot, such as disk perisistence
   for configuration files, event handler to handle the client/server
   connection, code to introspect modules for commands, deferred
   exception handling to not crash on an error, a parser to parse
   commandline options and values, etc.

   LIBOBJ also is a python3 bot, it can connect to IRC, fetch and
   display RSS feeds, take todo notes, keep a shopping list
   and log text. You can also copy/paste the service file and run
   it under systemd for 24/7 presence in a IRC channel.

   LIBOBJ is a contribution back to society and is Public Domain.


SYNOPSIS

::

   obj <cmd> [key=val] 
   obj <cmd> [key==val]
   obj [-c] [-d] [-v] [-i]


INSTALL

::

   $ pipx install libobj


USAGE

::

   default action is doing nothing

   $ obj
   $

   first argument is a command

   $ obj cmd
   cfg,cmd,dlt,dne,dpl,fnd,log,met,mod,mre,
   nme,pwd,rem,rss,sts,tdo,thr,ver

   starting a console requires an option

   $ obj -c
   >

   list of modules

   $ obj mod
   bsc,err,flt,irc,log,mod,rss,shp,sts,tdo,
   thr,udp

   if you want to run services like irc or rss,
   use the -i option

   $ obj -ci
   $

   start as daemon

   $ obj -d
   $ 

   add -v if you want to have verbose logging


CONFIGURATION

::

   irc

   $ bot cfg server=<server>
   $ bot cfg channel=<channel>
   $ bot cfg nick=<nick>

   sasl

   $ bot pwd <nsnick> <nspass>
   $ bot cfg password=<frompwd>

   rss

   $ bot rss <url>
   $ bot dpl <url> <item1,item2>
   $ bot rem <url>
   $ bot nme <url> <name>


COMMANDS

::

   cfg - irc configuration
   cmd - commands
   dlt - remove a user
   dne - mark todo as done
   dpl - sets display items
   fnd - find objects 
   log - log some text
   met - add a user
   mre - displays cached output
   nme - display name of a feed
   pwd - sasl nickserv name/pass
   rem - removes a rss feed
   rss - add a feed
   sts - show status
   tdo - add todo item
   thr - show the running threads


SYSTEMD

::

   replace "<user>" with the user running pipx
   save it in /etc/systems/system/libobj.service

   [Unit]
   Description=object library
   Requires=network.target
   After=network.target

   [Service]
   Type=simple
   User=<user>
   Group=<user>
   WorkingDirectory=/home/<user>/.obj
   ExecStart=/home/<user>/.local/pipx/venvs/libobj/bin/obj -d
   RemainAfterExit=yes

   [Install]
   WantedBy=multi-user.target


   run this

    $ sudo systemctl enable libobj --now


FILES

::

   ~/.bot
   ~/.local/bin/bot
   ~/.local/bin/botcmd
   ~/.local/bin/botd
   ~/.local/pipx/venvs/libbot/


AUTHOR

::

  libbot <libbotx@gmail.com>


COPYRIGHT

::

   LIBBOT is placed in the Public Domain.
