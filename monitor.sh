#!/usr/bin/env bash

if [ $(/bin/systemctl is-active sesame-autolocker) = "failed" ]; then
    /bin/systemctl start sesame-autolocker
    sleep 10
    if [ $(/bin/systemctl is-active sesame-autolocker) = "failed" ]; then
        /sbin/reboot
    fi
fi
