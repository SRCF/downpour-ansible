# Downpour Ansible

Downpour is an SRCF virtual machine running various "webapps". This repository
contains ansible config that sets up these webapps. Currently, this includes

 - Mattermost

## Overview

This only contains ansible roles for setting up the services. None are included
for setting up the server itself. Postgres and nginx are assumed to be
correctly setup, but individual playbooks are still expected to ensure they are
installed via apt.

A certbot role is also present to facilitate setting up certbot for the
subdomains of each webapp.
