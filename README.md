back-end
========

The basic idea here is to use [lamson](http://lamsonproject.org) in two parts:

* recieve email, check this is an alias exists, push message to queue
* watch the queue for new messages, push them into the DB

This will hopefully allow us fine tune the performance of either wwithout worrying about the other

Requires Lamson and Django

Join us in our IRC channel! We're in the #inboxen channel on [MegNet](https://www.megworld.co.uk/irc/)
