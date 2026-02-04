#!/bin/bash

USER_CHANGED=false

# Get current UID and GID of lf_admin user
CURRENT_UID=$(id -u lf_admin 2>/dev/null)
CURRENT_GID=$(id -g lf_admin 2>/dev/null)

# We want to allow both, USER_ID and PUID (the linuxserver.io convention)
if [ -n "$PUID" ]; then
    USER_ID=$PUID
fi
if [ -n "$PGID" ]; then
    GROUP_ID=$PGID
fi

# Only change group ID if it differs from target
# We set a default GROUP_ID in the Dockerfile.
if [ "$CURRENT_GID" != "$GROUP_ID" ]; then
    # echo "Changing lf_admin group ID to $GROUP_ID"
    groupmod -g $GROUP_ID lf_admin
    USER_CHANGED=true
fi

# Only change user ID if it differs from target
if [ "$CURRENT_UID" != "$USER_ID" ]; then
    # echo "Changing lf_admin user ID to $USER_ID"
    usermod -u $USER_ID -g $GROUP_ID lf_admin > /dev/null 2>&1
    USER_CHANGED=true
fi

# add additional groups
if [ -n "$EXTRA_GIDS" ]; then
    # Convert comma-separated values to space-separated
    EXTRA_GIDS=$(echo "$EXTRA_GIDS" | tr ',' ' ')
    for group in $EXTRA_GIDS; do
        # echo "Adding lf_admin to group $group"
        if ! getent group $group > /dev/null 2>&1; then
            groupadd -g $group lf_group_$group;
        fi;
        usermod -a -G $group lf_admin;
    done;
fi

if [ "$USER_CHANGED" = true ]; then
    # echo "Chaning permissions of /home/lf_admin"
    chown -R $USER_ID:$GROUP_ID /home/lf_admin
fi

# we use gosu over su to step down from root and avoid TTY issues
# https://github.com/tianon/gosu
exec gosu lf_admin "$@"
