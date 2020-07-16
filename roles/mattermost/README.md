# Overview

For the most part, this is a standard mattermost installation. However, since
we are too poor to pay for access control, we implement access control by
filtering requests at nginx, using
[lua-nginx-module](https://github.com/openresty/lua-nginx-module).

This allows for more fine-grained access control. For example, we allow sign
ups with any subdomain of `cam.ac.uk`, and users with an invitation can have
any email address. We also forbid non-administrators from modifying channel
properties such as descriptions, to allow for open channels.

All the magic is in `files/lua/mattermost.lua`.
